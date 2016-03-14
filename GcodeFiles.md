# Generating G-code files

Either fight it out with Inkscape, or use:
**http://doesliverpool.github.io/svgraph.html**

## Basic Instructions

1. Works best in CHROME browser.
1. Drag and drop your SVG file onto the screen **FIRST**.  This sets the scale.
1. (Alternatively to go from text, click on [svgize text] to make file from text box)
1. Use middle mouse scrollwheel to ZOOM on cursor.  There is no drag view!
1. Click on [MKstats] button to get the background drawing shape
1. Use Left Mouse Button to drag SVG data against the view, or Ctrl-Left Mouse to spin the shape (these features were designed for nesting)
1. Click [Save G-code] button to download fresh and thinned G-code, which you will then have to copy to the Beaglebone using scp

## Connected instructions

It's possible to get the G-code file to upload directly to the BB.

1. Log on to BB, go into "twistcodewiki" directory and run the script "pytwister".  This makes a webserver that listens on port 9003.
1. On the "svgraph.html" webpage, fill in the IPnumber for the BB and hit return.  If it works, this box will go green.  
1. The [MKstats] button will read the dimensions and status of the BB (in particular if it's running the Machinekit/Axis X-window application.
1. The [Send G-code] button will automatically upload and save g-code to a file called "/home/machinekit/gcodetwisted.ngc"
1. If the tickbox to the right is set, then it will attempt to autorun the g-code when it is uploaded.   (In the unlikely event this works, it won't redraw the picture on the Machinekit/Axis X-window

The webserver thing running on BB that holds the scripts is at https://bitbucket.org/goatchurch/twistcodewiki
Someone could replace it with a simple flask framework or something


