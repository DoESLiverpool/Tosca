# Generating G-code files

Either fight it out with Inkscape, or use:
**http://doesliverpool.github.io/svgraph.html**

## Resizing for the playing area instructions
1. The width needs to be put into the machinekit/tosca.hal file (find it and change it on the BB)
1. Home point origin (where you start from) is width\*0.5 down from the top left pulley, and then across by width\*0.5
1. Edit twistcodewiki/cgipipe/xylimits

## Poetry instructions
1. Log on to BB, go into "twistcodewiki" directory and run the script "pytwister".  This makes a webserver that listens on port 9003.
1. SSH Log on to BB again in another window, but with -X setting: cd machinekit \n . scripts/rip-environment \n machinekit tosca.ini
1. This calls up the axisUI controlling the maching.  Move to home position, click [home], load /home/machinekit/poetrygcode.ngc
1. Go to http://doesliverpool.github.io/svgraph.html, fill in the IP number into the box, hit return and it goes green
1. Type your poetry into "svgizing letters here" box, click [svgizetext].  This will relay the poetry directly to the BB which will gcode it in space available
1. Click "reload" icon on axisUI and now click on run icon
1. Last 3 steps will happen from a POST command to http://192.168.7.2:9003/cgipipe/genpoetry.py?centre=no' where the POST data is the ascii text of the poem with '\n' linefeeds.
1. This enables the 3-click poem of "export from Csharp", "reload in axisUI", "run in axisUI"

## Toxteth map instructions
1. SSH log on to BB with -X setting. and boot up axisUI
1. The files to plot will be in ../performancegcodes/*.ngc numbered in order
1. I will help lay out the map and the icons onto the map (position and scaling) using svgraph.html technology on Friday morning



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


