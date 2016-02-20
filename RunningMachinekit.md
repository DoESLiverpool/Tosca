# Getting Machinekit Running

This assumes you've already got a Beaglebone with Machinekit installed, but can be expanded as we get more detail on installing things.  It also assumes you have a computer running Linux to connect it to.

## Starting Machinekit
1. Plug the Beaglebone into the laptop with a USB cable
1. Connect to the Beaglebone
```
    ssh -X machinekit@192.168.7.2 
```

> If this doesn't work, then plug the Beaglebone onto the network with an Ethernet cable, and find its IP address via other means.  The Beaglebone only sets up the Ethernet on boot though, so you'll need to reboot it to fix that.

1. Log in with the password machinekit
1. Run the machinekit software.  This will spawn a new window on your laptop, which is actually running on the Beaglebone and just using your laptop as a display.
```
    cd machinekit
    . scripts/rip-environment
    machinekit mk7_bbb_pcb.ini
```

## Initialising Machinekit and the Polargraph

> This whole section should be simplified once we've got limit switches on the motor spools, as the homing will then do something useful

1. Set the correct kinematics to use
  1. Open the HAL Configuration view - from the menu "Machine" -> "Show HAL Configuration"
  1. Find the trivial kinematics in the tree on the left
  1. Type in the command to set it FIXME Check exactly where you type this
```
      setp kins-btrivial 1
```
1. ~~Home the machine~~ (that requirement has been removed for now)
  1. In the HAL Configuration window switch to the WATCH tab.
  1. Find the "all-home" and "probe-in" signals in the tree on the left and double(?)-click them to add them to the WATCH list
  1. Test the signals.  Try connecting the wire which is connected into one of the ground pins on the Beaglebone into each of the limit switch (P9-13) and probe-in (P9-15) pins on the Beaglebone.  When you connect it to one of the pins the corresponding signal in the WATCH list should turn yellow.
  1. If the signals are okay, we can proceed to home the machine.
  1. Enable the machine - click on the second(?) icon from the left on the toolbar.
  1. Set the feedrate really slow so it doesn't move much while you're homing it - around 10%
  1. Get ready to ground the limit switch signal like you did earlier, and then click the "Home all" button
  1. It will then try to home each axis in turn.  First the z-axis, which isn't connected to anything, then the others. For each axis you need to ground the limit switch signal twice - once to tell it its reached the end, and again once it has backed off and is coming in more slowly.  So *six times in all.*
1. Find the home point manually.  Using the cursor keys, move the pulleys round until you get to a sensible home position.
1. Type in the following Gcode command to set the current position to home.
```
g92x0y0
```

## Drawing something

1. Load a Gcode file, with "File" -> "Open"
1. [Optional] Manually jog to a starting point and set it as home with
```
g92x0y0
```
1. Click the play icon.


