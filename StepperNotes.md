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

On the Beaglebone the pin-outs are as follows:

 * P9-11 - the e-stop (ground it)
 * P9-29 - step (axis 0)
 * P9-31 - direction (axis 0)
 * P9-13 - home (pull high to **3.3V**, we think)

