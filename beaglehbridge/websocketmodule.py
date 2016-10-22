#!/usr/bin/env python3

import sys, socket, time, logging
import asyncio, websockets

def getipaddress():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

ipaddress = "localhost"
ipaddress = getipaddress()

mainasyncloop = asyncio.get_event_loop()
mainasyncloop.set_debug(True)

allwebsockets = set()
asyncqueueoutward = asyncio.Queue()
asyncqueueoutward.put_nowait("jjjj")
newwebsockets = asyncio.Queue()
asyncqueueinward = asyncio.Queue()

@asyncio.coroutine
def producer():
    while True:
        v = yield from asyncqueueoutward.get()
        for ws in list(allwebsockets):
            try:
                yield from ws.send(v)
            except websockets.exceptions.ConnectionClosed:
                print("remm", ws)
                allwebsockets.remove(ws)

@asyncio.coroutine
def receiverall():
    pendinglist = [ asyncio.async(newwebsockets.get()) ]
    rwebsockets = [ ]
    while True:
        done, pending = yield from asyncio.wait(pendinglist, return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            i = pendinglist.index(task)
            if i == 0:
                ws = task.result()
                rwebsockets.append(ws)
                pendinglist.append(asyncio.async(ws.recv()))
                pendinglist[0] = asyncio.async(newwebsockets.get())
            elif task.exception():
                del rwebsockets[i-1]
                del pendinglist[i]
            else:
                #print("mmm", [task.result()])
                asyncqueueinward.put_nowait(task.result())
                pendinglist[i] = asyncio.async(ws.recv())
        assert len(pendinglist) == len(rwebsockets)+1

posstring = "Nananana"
def setstartpositionstring(lposstring):
    global posstring
    posstring = lposstring
    
    
webconnectioncount = 0
@asyncio.coroutine
def handler(websocket, path):
    global webconnectioncount
    webconnectioncount += 1
    print("connected", websocket)
    allwebsockets.add(websocket)
    yield from newwebsockets.put(websocket)
    yield from asyncio.wait([websocket.send("Hello! #" + str(webconnectioncount))])
    yield from asyncio.wait([websocket.send(posstring)])
    try:
        while websocket in allwebsockets:
            yield from asyncio.sleep(10)
    finally:
        if websocket in allwebsockets:
            allwebsockets.remove(websocket)
        print("disconnecting", websocket)


def servewebsocketrunforever(portnumber):
    print("serving", ipaddress, portnumber)
    start_server = websockets.serve(handler, ipaddress, portnumber)
    mainasyncloop.run_until_complete(start_server)
    receivertask = asyncio.async(receiverall())
    producertask = asyncio.async(producer())
    mainasyncloop.run_forever()

    

