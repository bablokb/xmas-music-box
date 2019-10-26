A music box for Christmas
=========================


This is a music box for Christmas with lights, a turning figure and music.

It is  based on the following compontents:

  - Trinket-M0 (microcontroller running CircuitPython)
  - a NeoPixels-ring
  - a DFPlayer-Mini (simplistic MP3-player)
  - and a servo motor

Currently, this is work in progress. The "simple implementation" (see below)
is fully functional.


Hardware
--------

The M0 controls the NeoPixel-ring and starts the continuous server-motor as well as
the player. Two additional buttons are directly attached to the player to let
the user control the volume and skip to the next or previous song.


Software
--------

You need the following CircuitPython-libs from the library-bundle:

  - neopixel
  - adafruit_motor


Simple Implementation
---------------------

The simple implementation will run some light effects, start the servo-motor
and play the songs on the SD-Card. The M0 will monitor the busy-state of the
player and skip to the next song after a song has finished.

Used M0-Pins:

  - 0: PWM for the servo-motor
  - 1: Attached to the next/vol+-pin of the player
  - 2: Data-pin of the NeoPixel-ring
  - 3: Attached to the busy-pin of the player
  - 4: Configured as capacitive input-button for turning everything on and off

Copy the contents of the directory `simple/files` to your Trinket and add the
required libraries.

In `simple/doc` you will find the required wiring.

