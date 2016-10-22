#!/usr/bin/env python3

import threading, time, re

from websocketmodule import mainasyncloop, servewebsocketrunforever, asyncqueueoutward, asyncqueueinward
from websocketmodule import setstartpositionstring

from motorcontrolmodule import arm, pwm0, pwm1, memp0, memp1, PolarPos
qdistcutoff = 2000

polarpos = PolarPos(arm, [(memp0, pwm0), (memp1, pwm1)])

#help(asyncqueueinward)
def motiondutyfunction():
    polax = [pa.qpos for pa in polarpos.polaraxes]
    #polax = [pa.qstart for pa in polarpos.polaraxes]
    setstartpositionstring("start X%dY%d" % tuple(polax))

    tS = time.time()
    prevpolax = [0, 0]
    while True:
        if asyncqueueinward.qsize() > 0:
            svall = asyncqueueinward.get_nowait()
            comm, sval = svall.split(maxsplit=1)
            if comm == "pt":
                mval = re.search("X([\-\d\.]+)Y([\-\d\.]+)", sval)
                polarpos.polaraxes[0].qdestination = int(mval.group(1))
                polarpos.polaraxes[1].qdestination = int(mval.group(2))
                print("goto", [pa.qdestination for pa in polarpos.polaraxes])
            else:
                print("kkk", [svall])
        polarpos.readeqeps()
        polax = [pa.qpos for pa in polarpos.polaraxes]
        if polax != prevpolax:
            mainasyncloop.call_soon_threadsafe(asyncqueueoutward.put_nowait, "cpt X%dY%d" % tuple(polax))
            prevpolax = polax
        if max(abs(pa.qpos-pa.qstart)  for pa in polarpos.polaraxes) > qdistcutoff:
            print("too far shutting down")
            exit()
        
        polarpos.updateduty()
        ltS = time.time()
        if ltS - tS > 15:
            tS = ltS
            print([pa.qpos for pa in polarpos.polaraxes], [pa.qdestination for pa in polarpos.polaraxes], ["%.3f"%pa.qvolts for pa in polarpos.polaraxes], ["%.3f"%pa.qsumerror for pa in polarpos.polaraxes], ["%.3f"%pa.dc for pa in polarpos.polaraxes])



motiondutythread = threading.Thread(target=motiondutyfunction)
motiondutythread.setDaemon(True)
motiondutythread.start()    

servewebsocketrunforever(5678)


