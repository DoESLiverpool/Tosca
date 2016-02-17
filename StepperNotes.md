# Stepper Version Notes

Notes on the version using the TLRN steppers.

They have [BigEasyDriver boards](http://SchmalzHaus.com/BigEasyDriver) to run the steppers.  On the existing wiring, the colour coding is as follows:
 * White - direction
 * Blue - step
 * Green - sleep
 * Red - Vcc
 * Black - Ground

Pin mapping is in the .hal file.

If you ground pin P9-11, that disables the e-stop.

log on with
ssh -X machinekit@192.168.7.2 pw: machinekit
cd machinekit
. scripts/rip-environment
machinekit mk7_bbb_pcb.ini

You can see the signals if you do machine -> show hal configuration

On the Beaglebone the pin-outs are as follows:
https://graycat.io/wp-content/uploads/2012/12/beaglebone_pinout.png

according to mk7_bbb_pcb.hal:
 * P9-11 - estop connect to Ground
 * P9-13 - limit switch connect to Ground 3 times during the homing cycle (before you can load an G-code)
 * P9-15 - probe-in (connect to ground to show it light up)
  
 * P9-29 - step (axis 0)
 * P9-31 - direction (axis 0)
 * P9-28 - direction (axis 1)
 * P9-30 - step (axis 1)

