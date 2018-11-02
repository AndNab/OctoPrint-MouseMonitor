# OctoPrint-Spool-Sensor
Detect loss of spool movement to automatically pause a print job

## Description

As an avid hobbyist in the 3D printing space, I believed for my first year doing this that *filament runout* was important so that prints could be successful. I've come to learn that runout is a subset of the bigger picture. The real problem is **filament delivery**. If you can detect that the print spool is no longer moving, you can now detect a variety of problems:

* simple end-of-roll loss of filament
* spool sticking to manufacturer’s poorly-designed spool holder
* cross-threading of the filament on the roll
* hot-spooling the filament at the factory which resulted in filament which sticks together
* filament like carbon fiber—infused which likes to stick to itself
* old filament which is now brittle and breaks as a result
* overall poor design of the spool (boxy) shape itself, resulting in cross-threading
* overall poor design of the filament delivery path itself, resulting in too much force needed to extrude and notching at the bowden gear
* filament thickness quality issues as combined with PTFE feed tubing, resulting in stuck filament in the tube and notching at the bowden gear
* too-flexible filament as combined with any of the conditions above, resulting in filament notching at the bowden gear
* z-offset too close to the bed, resulting in hotend jamming and notching at the bowden gear
* poor first-layer adhesion, leading to a build-up of filament and ultimate hotend jamming and notching at the bowden gear

So it's not just about filament runout through a detector switch. Anything that prevents filament movement should be dealt with promptly so that corrective action may be taken by the operator.

## Overview

This is an [OctoPrint](http://octoprint.org/) plugin which integrates with a standard serial computer mouse and is used as a filament movement sensor. The mouse is connected to a Raspberry Pi via USB and the code may then detect when the spool is moving or not during a print job.

## Required recycled hardware and 3D-printed parts

Using this plugin requires some 3D printed parts as well as a semi-dedicated USB- or Bluetooth-based computer mouse. No modifications are done to the mouse so you could technically use this in a temporary status if you wanted. Just leave it connected while the plugin is enabled, however.

![img_0118](https://user-images.githubusercontent.com/15971213/47886367-c9ac3680-ddf6-11e8-8d61-9d9db6eb5dfb.JPG)

I assume that you're using some sort of print spool holder which is smaller in diameter than about 30mm, the ID of the printed mouse assembly's hole.

![spoolholderwithbracket](https://user-images.githubusercontent.com/15971213/47886320-8ce03f80-ddf6-11e8-8675-bdd975a7fc43.png)

Finally, it will be necessary to install the Raspbian Desktop first as part of the dependency stack. (See below.)

## Features

* Inexpensive hardware (Dell USB Scroll 3 Button Optical Mouse)
* Two plastic parts to be printed
* Execution of custom GCODE when no spool movement is detected
* Optionally pause print when no spool movement is detected
* The code should capture the mouse's events so that they don't bubble up to the Raspbian Desktop if you are running a local display

## Installation

### Hardware
Installing the sensor involves 3D printing the parts, assembling them with a hex head bolt having trapped the mouse between them.

* Slice [SpoolSensorBottom.stl](https://raw.githubusercontent.com/OutsourcedGuru/OctoPrint-Spool-Sensor/master/3d-parts/SpoolSensorBottom.stl) with Cura, for example, upload to OctoPrint and print it
* Slice [SpoolSensorLidCurved.stl](https://raw.githubusercontent.com/OutsourcedGuru/OctoPrint-Spool-Sensor/master/3d-parts/SpoolSensorLidCurved.stl) with Cura, for example, upload to OctoPrint and print it
* One [aluminum hex head 6-32 bolt @ 3/8"](https://www.servocity.com/6-32-zinc-plated-socket-head-machine-screws) plus the appropriate hex wrench which fits it as seen [here](https://www.servocity.com/actobotics-hardware-pack-a)
* [Dell M0C5U0 USB Scroll 3 Button Optical Mouse 0XN967](https://www.amazon.com/Dell-M0C5U0-Scroll-Button-Optical/dp/B004XUGYMQ?SubscriptionId=AKIAILSHYYTFIVPWUY6Q&tag=duckduckgo-osx-20&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B004XUGYMQ) (or nearly identical to shape and height)

#### Slicing details for both parts
* Standard PLA (195°C)
* Rotate lid so that curve on bottom side faces upward
* Infill 25%, tri-hexagon
* No build plate adhesion nor support
* 0.2mm layer height or similar
* Special Mode: Relative extrusion recommended but optional

### Printed detection sheet
Print this on standard 8.5" x 11" paper, cut a hole in the center to accommodate your spool holder. Cut a large circle from the center and mount this between your spool and the 3D-printed mouse holder. When the spool turns, the paper should also turn. See the next photo.

![checkerboard-paper-printable](https://user-images.githubusercontent.com/15971213/47885301-9024fc80-ddf1-11e8-8b4a-b64b25e95c13.png)

Here's the basic assembly of the detector sheet as trapped between the spool and the mouse assembly.

![img_0119](https://user-images.githubusercontent.com/15971213/47885553-e47cac00-ddf2-11e8-99e0-2b22c27db9c2.JPG)

The mouse may be inserted in either orientation. The plugin should detect spool movement either way. It may be necessary to insert a folded shim of paper so that the mouse doesn't move within the assembly. The light under the mouse should be centered within the hole for this to work well. Tighten the bolt when everything is in place and snug the assembly against the spool.

### Software

As an initial step, it may be necessary to first install the Raspbian Desktop from the `~/scripts` folder, having remoted into your Raspberry Pi. The `PyUserInput` Python module requires this as a dependency. Run `~/scripts/install-desktop` and reboot when it is finished.

In **OctoPrint** -> **Settings** -> **Plugin Manager** -> **Get More...** -> **...from URL** -> `https://github.com/OutsourcedGuru/Octoprint-Spool-Sensor/archive/master.zip` -> **Install**

## Configuration

After installation, configure the plugin via **OctoPrint** -> **Settings** -> **Plugins** -> **Spool Sensor** settings dialog.
