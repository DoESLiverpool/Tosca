
from mmap import mmap
import time, struct, sys, ctypes, select, threading, socket, re, atexit
from Adafruit_BBIO import PWM
from Adafruit_BBIO import GPIO

print("hi there", __name__)

portnumber = 9019
qdistcutoff = 2000

# load the capes for the eqeps using:
# echo bone_eqep0 > /sys/devices/bone_capemgr*/slots
# echo bone_eqep1 > /sys/devices/bone_capemgr*/slots


arm = "P9_12"
pwm0 = "P9_16"
pwm1 = "P9_21"
pwm2 = "P9_14"


PWMSS0_offset = 0x48300000
PWMSS0_size = 0x4830025F - PWMSS0_offset + 1
PWMSS1_offset = 0x48302000
PWMSS1_size = 0x4830225F - PWMSS1_offset + 1
PWMSS2_offset = 0x48304000
PWMSS2_size = 0x4830425F - PWMSS2_offset + 1

fp = open("/dev/mem", "r+b" )
memp0 = mmap(fp.fileno(), PWMSS0_size, offset=PWMSS0_offset)
memp1 = mmap(fp.fileno(), PWMSS1_size, offset=PWMSS1_offset)
#memp2 = mmap(fp.fileno(), PWMSS2_size, offset=PWMSS2_offset)
QPOSCNT = 0x180 + 0x00
QCAPCTL = 0x180 + 0x2C
memp0[QCAPCTL:QCAPCTL+4] = struct.pack("<L", 0x8000)
memp1[QCAPCTL:QCAPCTL+4] = struct.pack("<L", 0x8000)
#memp2[QCAPCTL:QCAPCTL+4] = struct.pack("<L", 0x8000)

class PolarAxis:
    def __init__(self, memp, pwm):
        self.memp = memp
        self.pwm = pwm
        self.qpos = 0
        self.qstart = None
        self.qdestination = None
        self.qsumerror = 0
        self.qvolts = 0
        self.dc = 0
        
    def readeqep(self):
        self.qpos = struct.unpack("<l", self.memp[QPOSCNT:QPOSCNT+4])[0]
        if self.qstart is None:
            self.qstart = self.qpos
            self.qdestination = self.qpos

    def updatevolts(self, dt):
        if self.qdestination is None:
            self.qvolts = 50
            return
        d = self.qdestination - self.qpos
        if abs(d) > 900:
            self.qsumerror = 0
        else:
            self.qsumerror += d*dt*0.001
            self.qvolts = -d*0.01 - self.qsumerror*6
            
    def updateduty(self, t0):
        modpunch = int(t0*200) % 8
        bpunch = (modpunch <= 0) if abs(self.qvolts) > 3.1 else (modpunch <= 2)
        fac = 3 if bpunch else 1
        bnds = 25 if bpunch else 15
        dc = max(-bnds, min(bnds, self.qvolts*fac))
        self.dc = dc+50
        PWM.set_duty_cycle(self.pwm, dc+50)

class PolarPos:
    def __init__(self, arm, axes):
        self.arm = arm
        self.polaraxes = [ PolarAxis(memp, pwm)  for memp, pwm in axes ]
        self.updatedutycount = 0
        self.t0 = time.time()
        
        if self.arm:
            GPIO.setup(self.arm, GPIO.OUT)
            GPIO.output(self.arm, GPIO.LOW)
        for memp, pwm in axes:
            if pwm:
                print("starting", pwm)
                PWM.start(pwm, 50, 100000, 1)
        if self.arm:
            GPIO.output(self.arm, GPIO.HIGH)

        def settostationary(armaxes):
            arm, axes = armaxes
            if arm:
                GPIO.output(arm, GPIO.LOW)
            for memp, pwm in axes:
                print("set stationary", pwm, arm)
                if pwm:
                    PWM.start(pwm, 50, 100000, 1)
        atexit.register(settostationary, (arm, axes))  # values kept here by closure
        self.readeqeps()

    def readeqeps(self):    
        for pa in self.polaraxes:
            pa.readeqep()

    def updateduty(self):
        self.updatedutycount += 1
        t1 = time.time()
        dt = t1 - self.t0
        self.t0 = t1
        for pa in self.polaraxes:
            pa.updatevolts(dt)
            pa.updateduty(t1)


stdincommand = 'c'
def readstdin():
    global stdincommand
    while True:
        c = sys.stdin.read(1)
        if c == 'q':
            stdincommand  = c

input_thread = threading.Thread(target=readstdin)
input_thread.setDaemon(True)
input_thread.start()

def readhttp(polarpos):
    global ccommand, qp
    
    # find the ip address we are working from
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipaddress = s.getsockname()[0]
    
    # now make the connection
    print("serving on %s:%s" % (ipaddress, portnumber))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ipaddress, portnumber))
    s.listen(1)
    connectioncount = 0
    
    while True:
        connectioncount += 1
        #print("waiting for connection", connectioncount)
        conn, address = s.accept()
        buf = conn.recv(1024)
        #print("received ", len(buf), buf)
        posvals = ",".join(str(pa.qpos)  for pa in polarpos.polaraxes)
        data = "pos(%s,%d);\n" % (posvals, polarpos.updatedutycount)
        
        mxy = re.match("GET /x([0-9\-\.]+)y([0-9\-\.]+)", buf)
        if mxy:
            if len(polarpos.polaraxes) >= 1:
                polarpos.polaraxes[0].qdestination = int(mxy.group(1))
            if len(polarpos.polaraxes) >= 2:
                polarpos.polaraxes[1].qdestination = int(mxy.group(2))
            print("goingto", [pa.qdestination for pa in polarpos.polaraxes])

        
        conn.send('HTTP/1.0 200 OK\r\n')
        conn.send('Connection: close\r\n')
        conn.send('Content-Length: %d\r\n' % len(data))
        conn.send('Content-Type: text/html\r\n')
        conn.send('\r\n')
        try:
            conn.send(data)
            conn.close()
        except:
            pass
        

if __name__ == "__main__":
    polarpos = PolarPos(arm, [(memp1, pwm0), (memp0, pwm1)])
    http_thread = threading.Thread(target=readhttp, args=(polarpos,))
    http_thread.setDaemon(True)
    http_thread.start()
    
    tS = time.time()
    
    while True:
        polarpos.readeqeps()
        if max(abs(pa.qpos-pa.qstart)  for pa in polarpos.polaraxes) > qdistcutoff:
            print("too far shutting down")
            break
        
        polarpos.updateduty()
        ltS = time.time()
        if ltS - tS > 1:
            tS = ltS
            print([pa.qpos for pa in polarpos.polaraxes], [pa.qdestination for pa in polarpos.polaraxes], ["%.3f"%pa.qvolts for pa in polarpos.polaraxes], ["%.3f"%pa.qsumerror for pa in polarpos.polaraxes], ["%.3f"%pa.dc for pa in polarpos.polaraxes])
        if stdincommand == 'q':
            sys.exit(0)

