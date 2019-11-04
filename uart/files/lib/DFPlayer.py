# ----------------------------------------------------------------------------
# CircuitPython driver library for the DFPlayer-Mini.
#
# The core of the code is from: https://github.com/jczic/KT403A-MP3 
# (adapted to CircuitPython, changed naming, stripped down API)
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/circuitpython-dfplayer
#
# ----------------------------------------------------------------------------

import board
import time
import busio
import struct

class DFPlayer(object):

  # --- constants   ----------------------------------------------------------

  MEDIA_U_DISK = 1
  MEDIA_SD     = 2
  MEDIA_AUX    = 3
  MEDIA_SLEEP  = 4
  MEDIA_FLASH  = 5

  EQ_NORMAL     = 0
  EQ_POP        = 1
  EQ_ROCK       = 2
  EQ_JAZZ       = 3
  EQ_CLASSIC    = 4
  EQ_BASS       = 5

  STATUS_STOPPED = 0x0200
  STATUS_BUSY    = 0x0201
  STATUS_PAUSED  = 0x0202

  # --- constructor   --------------------------------------------------------

  def __init__(self,uart=None,media=None,volume=50,eq=None,latency=0.100):
    if uart is None:
      self._uart = busio.UART(board.TX,board.RX,baudrate=9600)
    else:
      self._uart = uart
    self._latency = latency
    self.set_media(media if media else DFPlayer.MEDIA_SD)
    if not self.get_status():
      raise Exception('DFPlayer could not be initialized.')
    self.set_volume(volume)
    self.set_eq(eq if eq else DFPlayer.EQ_NORMAL)

  # --- transfer data to device   ---------------------------------------------

  def _write_data(self, cmd, dataL=0, dataH=0):
    self._uart.write(b'\x7E')        # Start
    self._uart.write(b'\xFF')        # Firmware version
    self._uart.write(b'\x06')        # Command length
    self._uart.write(bytes([cmd]))   # Command word
    self._uart.write(b'\x00')        # Feedback flag
    self._uart.write(bytes([dataH])) # DataH
    self._uart.write(bytes([dataL])) # DataL
    self._uart.write(b'\xEF')        # Stop

    # give device some time
    if cmd == 0x09:                        # set_media
      time.sleep(0.200)
    elif cmd == 0x0C:                      # reset
      time.sleep(1.000)
    elif cmd in [0x47,0x48,0x49,0x4E]:     # query files
      time.sleep(0.500)
    else:
      time.sleep(self._latency)            # other commands

  # --- read data from device   ------------------------------------------------

  def _read_data(self):
    if True: #self._uart.in_waiting:
      buf = self._uart.read(10)
      if buf is not None and \
             len(buf) ==   10 and \
             buf[0]   == 0x7E and \
             buf[1]   == 0xFF and \
             buf[2]   == 0x06 and \
             buf[9]   == 0xEF:
        cmd  = buf[3]
        data = struct.unpack('>H', buf[5:7])[0]
        return (cmd, data)
      return None

  # --- get response   ---------------------------------------------------------

  def _read_response(self):
    res = None
    while True:
      r = self._read_data()
      if not r:
        return res
      res = r

  # --- play   -----------------------------------------------------------------

  def play(self,folder=None,track=None):
    if folder is None and track is None:
      self._write_data(0x0D)
    elif folder is None:
      self._write_data(0x03,int(track%256),int(track/256))
    elif track is None:
      self._write_data(0x12,folder)
    else:
      self._write_data(0x0F,track,folder)

  # --- pause   ----------------------------------------------------------------

  def pause(self):
    self._write_data(0x0E)

  # --- stop   -----------------------------------------------------------------

  def stop(self):
    self._write_data(0x16)

  # --- play next song   -------------------------------------------------------

  def next(self):
    self._write_data(0x01)

  # --- set media device   -----------------------------------------------------

  def set_media(self,media):
    self._media = media
    self._write_data(0x09, media)

  # --- set volume   -----------------------------------------------------------

  def set_volume(self,percent):
    if percent < 0:
      percent = 0
    elif percent > 100:
      percent = 100
    self._write_data(0x06, int(percent*0x1E/100))

  # --- set equalizer   --------------------------------------------------------

  def set_eq(self,eq):
    if eq < 0 or eq > 5:
      eq = 0
    self._write_data(0x07,eq)

  # --- switch to low power state   --------------------------------------------

  def set_standby(self,on=True):
    if on:
      self._write_data(0x0A)
    else:
      self._write_data(0x0B)

  # --- reset chip   -----------------------------------------------------------

  def reset(self):
    self._write_data(0x0C)

  # --- read busy state   ------------------------------------------------------

  def get_status(self):
    self._write_data(0x42)
    r = self._read_response()
    return r[1] if r and r[0] == 0x42 else None
