# Getting Machinekit Running

This assumes you've already got a Beaglebone with Machinekit installed, but can be expanded as we get more detail on installing things.  It also assumes you have a computer running Linux to connect it to.

## Starting Machinekit
1. Plug the Beaglebone into the laptop with a USB cable
1. Connect to the Beaglebone
  ```
  ssh -X machinekit@192.168.7.2 
  ```

  > If this doesn't work, then plug the Beaglebone onto the network with an Ethernet cable, and find its IP address via other means.  The Beaglebone only sets up the Ethernet on boot though, so you'll need to reboot it to fix that.

1. Connect through the network to the BB by running:  nmap -p22 192.168.0.255/24 and look for something that is open to get the ipnumber  (this should be fixed by https://github.com/DoESLiverpool/Tosca/issues/27 )
1. Log in machinekit@192.168.0.130 with the password machinekit over the network (or 192.168.7.2 if over the USB ssh over serial)
1. Run the machinekit software.  This will spawn a new window on your laptop, which is actually running on the Beaglebone and just using your laptop as a display.
  ```
  cd machinekit
  . scripts/rip-environment
  machinekit mk7_bbb_pcb.ini
  ```
1. Home the machine by using left right up down cursor keys to put the pen in the middle of the board with both strings at right angles to each other.  Click on "home all"
1. Type in the following Gcode command to set the current position to home.
  ```
  g92x0y0
  ```

## Drawing something

1. Load a Gcode file, with "File" -> "Open"
1. For example, go up one directory and load bighelloworld.ngc
1. [Optional] Manually jog to a starting point and set it as home with
  ```
  g92x0y0
  ```
1. Control the speed with manual Feed override and max velocity (for the "retracted" linking moves) 
1. Click the play icon.


