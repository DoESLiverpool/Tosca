
from mmap import mmap
import time, struct, sys, ctypes, select, threading, socket, re, atexit
from Adafruit_BBIO import PWM
from Adafruit_BBIO import GPIO


arm = "P9_12"
pwm0 = "P9_16"
pwm1 = "P9_21"
pwm2 = "P9_14"

PWM.start(pwm0, 50, 100000, 1)
PWM.start(pwm1, 50, 100000, 1)


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
QCPRD   = 0x180 + 0x3C
memp0[QCAPCTL:QCAPCTL+4] = struct.pack("<L", 0x8000)
memp1[QCAPCTL:QCAPCTL+4] = struct.pack("<L", 0x8000)
#memp2[QCAPCTL:QCAPCTL+4] = struct.pack("<L", 0x8000)

memp, pwm = memp1, pwm1
memp, pwm = memp0, pwm0
dc = 55

def getq():
    return struct.unpack("<l", memp[QPOSCNT:QPOSCNT+4])[0]
def getprd():
    return struct.unpack("<L", memp[QCPRD:QCPRD+4])[0]&0xFFFF



qpos0 = getq()
print("starting point is " + str(qpos0))

GPIO.setup(arm, GPIO.OUT)
GPIO.output(arm, GPIO.LOW)
GPIO.output(arm, GPIO.HIGH)


timX = time.time()
PWM.set_duty_cycle(pwm, dc)

posx = [ ]
while len(posx) < 10000:
    dt = time.time() - timX
    if dt > 3:
        break
    dq = getq() - qpos0
    if abs(dq) > 500:
        PWM.set_duty_cycle(pwm, 50)
    posx.append((int(dt*1000000), dq, getprd()))
PWM.set_duty_cycle(pwm, 50)
GPIO.output(arm, GPIO.LOW)
print(posx[::100])

