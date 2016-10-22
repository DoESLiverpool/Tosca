#!/usr/bin/env python3

from mmap import mmap
import time, struct, sys, re, atexit, math
from Adafruit_BBIO import PWM
from Adafruit_BBIO import GPIO


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

T0 = time.time()

class PolarAxis:
    def __init__(self, memp, pwm):
        self.memp = memp
        self.pwm = pwm
        self.qpos = 0
        self.qstart = None
        self.qdestination = None
        self.qsumerror = 0
        self.qvolts = 0
        self.dc = 50
        
    def readeqep(self):
        self.qpos = struct.unpack("<l", self.memp[QPOSCNT:QPOSCNT+4])[0]

        # fake eqep data
        t = int((time.time() - T0)*10)/10
        self.qpos = 20 + int(360*(math.sin(t) if self.pwm == pwm0 else math.cos(t)))

        if self.qstart is None:
            self.qstart = self.qpos
            self.qdestination = self.qpos

    def updatevolts(self, dt):
        if self.qdestination is None:
            self.qvolts = 0
            return
        d = self.qdestination - self.qpos
        if abs(d) > 900:
            self.qsumerror = 0
        else:
            self.qsumerror += d*dt*0.001
            self.qvolts = -d*0.01 - self.qsumerror*6
            
    def updateduty(self, t1):
        bnds = 5
        fac = 1
        dc = max(-bnds, min(bnds, self.qvolts*fac))
        self.dc = dc+50
        PWM.set_duty_cycle(self.pwm, self.dc)

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

        
