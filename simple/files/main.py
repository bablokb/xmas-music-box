# -------------------------------------------------------------------------
# Control NeoPixel-ring, servo-motor and dfplayer-mini
#
# Note that you have to add neopixel.mpy and adafruit_motor from the
# library-bundle corresponding to your version of CircuitPython on the M0.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/trinket-m0
#
# -------------------------------------------------------------------------

import time
import board
import neopixel
import pulseio
import touchio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_motor import servo

# --- helper class for NeoPixel rainbow   ----------------------------------
# (copied and modified from Adafruit's exsamples)

class Rainbow(object):
  def __init__(self,pin,num_pixels):
    self._pin        = pin
    self._num_pixels = num_pixels
    self._pixels     = neopixel.NeoPixel(pin,num_pixels,
                           pixel_order=neopixel.GRBW,
                           brightness=0.05, auto_write=False)
    self._state  = -1

  def wheel(self,pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3, 0)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3, 0)

  def update(self):
    """ update the state of the rainbow """
    self._state = (self._state + 1) % 255
    for i in range(self._num_pixels):
      rc_index = (i * 256 // self._num_pixels) + self._state
      self._pixels[i] = self.wheel(rc_index & 255)
    self._pixels.show()
    # Adafruit's code sleeps here, we sleep in the main-loop instead

  def off(self):
    """ turn off all pixels """
    self._state = -1
    for i in range(self._num_pixels):
      self._pixels[i] = (0,0,0,0)
    self._pixels.show()
    
# --- constants   ----------------------------------------------------------

NUM_PIXEL    = 24
PIXEL_PIN    = board.D2

SERVO_PIN    = board.D0
SERVO_STOP   = -0.05
SERVO_GO     = -0.15

DFP_NEXT_PIN = board.D1
DFP_BUSY_PIN = board.D3

TOUCH_PIN    = board.D4

# --- objects   -----------------------------------------------------------

rainbow = Rainbow(PIXEL_PIN,NUM_PIXEL)           # NeoPixel control object

dfp_next           = DigitalInOut(DFP_NEXT_PIN)  # connect to IO2 of dfplayer
dfp_next.direction = Direction.OUTPUT
dfp_busy           = DigitalInOut(DFP_BUSY_PIN)  # connect to BUSY of dfplayer
dfp_busy.direction = Direction.INPUT

touch              = touchio.TouchIn(TOUCH_PIN)  # direct use as touch-button

pwm   = pulseio.PWMOut(SERVO_PIN,frequency=50)   # connect to servo-motor
servo = servo.ContinuousServo(pwm)               # servo-motor control object

# --- initialization   ----------------------------------------------------

active         = True
servo.throttle = SERVO_GO

# --- main loop   --------------------------------------------------------

while True:
  if active:
    rainbow.update()
    if dfp_busy.value:             # high: not playing: skip to next song
      print("switching to next song")
      dfp_next.value = 0
      time.sleep(0.1)
      dfp_next.value = 1
      time.sleep(0.1)              # dfplayer needs some time to start next song
  
  if touch.value:
    print("registered touch")
    time.sleep(0.1)                # debounce
    if active:
      print("stopping neopixels and servo (current song will finish)")
      active         = False
      servo.throttle = SERVO_STOP
      rainbow.off()
    else:
      print("starting neopixels and servo")
      active         = True
      servo.throttle = SERVO_GO

  time.sleep(0.1)
