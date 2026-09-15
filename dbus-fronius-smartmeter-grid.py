#!/usr/bin/env python

"""
Created by Ralf Zimmermann (mail@ralfzimmermann.de) in 2020, amended by Ben De Longis (unifiedcommsguy@gmail.com) in June 2021 to include following features:

- External config file config.py
- Support for all fields in VenusOS Screen (including Power/Current etc)
- Support for single phase meters

This code can be found: https://github.com/unifiedcommsguy/victron-dbus-fronius-smartmeter

Credit to Ralf Zimmermann - https://github.com/RalfZim/venus.dbus-fronius-smartmeter
Used https://github.com/victronenergy/velib_python/blob/master/dbusdummyservice.py as basis for this service.
Reading information from the Fronius Smart Meter via http REST API and puts the info on dbus.
"""
import config as cfg # import config.py file
from gi.repository import GLib
import platform
import logging
import sys
import os
import requests # for http GET
import _thread as thread   # for daemon = True

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../ext/velib_python'))
from vedbus import VeDbusService

class DbusDummyService:
  def __init__(self, servicename, deviceinstance, paths, productname='Fronius Smart Meter', connection='Fronius Smart Meter service'):

    self._gridbusservice = VeDbusService(servicename)
    self._paths = paths

    logging.debug("%s /DeviceInstance = %d" % (servicename, deviceinstance))

    self._gridbusservice.add_path('/Mgmt/Connection', 'Fronius Virtual Grid Meter service')
    self._gridbusservice.add_path('/ProductName', 'Fronius Virtual Grid Meter')
    self._gridbusservice.add_path('/DeviceInstance', 40)

    for service in [self._gridbusservice]:
      # Create the management objects, as specified in the ccgx dbus-api document
      service.add_path('/Mgmt/ProcessName', __file__)
      service.add_path('/Mgmt/ProcessVersion', 'Unkown version, and running on Python ' + platform.python_version())

      # Create the mandatory objects
      service.add_path('/ProductId', 45058) # value used in ac_sensor_bridge.cpp of dbus-cgwacs
      service.add_path('/FirmwareVersion', 0.1)
      service.add_path('/HardwareVersion', 0)
      service.add_path('/Connected', 1)

      for path, settings in self._paths.items():
        service.add_path(
          path, settings['initial'], writeable=True, onchangecallback=self._handlechangedvalue)

    GLib.timeout_add(cfg.fronius_smartmeter["interval"], self._update) # pause before the next request

  def _update(self):
    URL = "http://" + cfg.fronius_smartmeter["ipaddress"] + "/solar_api/v1/GetMeterRealtimeData.cgi?Scope=Device&DeviceId=0&DataCollection=MeterRealtimeData"
    meter_r = requests.get(url = URL)
    meter_data = meter_r.json()
    data = meter_data['Body']['Data']

    URL = "http://" + cfg.fronius_pvinverter["ipaddress"] + "/solar_api/v1/GetPowerFlowRealtimeData.fcgi?Scope=System"
    meter_r_pv = requests.get(url=URL)
    pvmeter_data = meter_r_pv.json()
    site_data = pvmeter_data['Body']['Data']['Site']

    # Common Items
    MeterConsumption = -float(data.get('PowerReal_P_Sum', 0))
    #self._acloaddbusservice['/Ac/Power'] = MeterConsumption
    #self._acloaddbusservice['/Ac/Current'] = float(data.get('Current_AC_Sum', 0))
    #self._acloaddbusservice['/Ac/Energy/Forward'] = float(data.get('EnergyReal_WAC_Sum_Consumed', 0)) / 1000
    #self._acloaddbusservice['/Ac/Energy/Reverse'] = float(data.get('EnergyReal_WAC_Sum_Produced', 0)) / 1000
    
    # Phase 1
    #self._acloaddbusservice['/Ac/L1/Voltage'] = float(data.get('Voltage_AC_Phase_1', 0))
    #self._acloaddbusservice['/Ac/L1/Current'] = float(data.get('Current_AC_Phase_1', 0))
    #self._acloaddbusservice['/Ac/L1/Power'] = -float(data.get('PowerReal_P_Phase_1', 0))
    #self._acloaddbusservice['/Ac/L1/Energy/Forward'] = float(data.get('EnergyReal_WAC_Sum_Consumed', 0)) / 1000
    #self._acloaddbusservice['/Ac/L1/Energy/Reverse'] = float(data.get('EnergyReal_WAC_Sum_Produced', 0)) / 1000

    #if cfg.fronius_smartmeter["numphases"] == 1:
      #self._acloaddbusservice['/Ac/L2/Voltage'] = 0.0
      #self._acloaddbusservice['/Ac/L3/Voltage'] = 0.0
      #self._acloaddbusservice['/Ac/L2/Current'] = 0.0
      #self._acloaddbusservice['/Ac/L3/Current'] = 0.0
      #self._acloaddbusservice['/Ac/L2/Power'] = 0.0
      #self._acloaddbusservice['/Ac/L3/Power'] = 0.0
      #self._acloaddbusservice['/Ac/L2/Energy/Forward'] = 0.0
      #self._acloaddbusservice['/Ac/L2/Energy/Reverse'] = 0.0
      #self._acloaddbusservice['/Ac/L3/Energy/Forward'] = 0.0
      #self._acloaddbusservice['/Ac/L3/Energy/Reverse'] = 0.0
    #else:
      # Phase 2 & 3
      #self._acloaddbusservice['/Ac/L2/Voltage'] = float(data.get('Voltage_AC_Phase_2', 0))
      #self._acloaddbusservice['/Ac/L3/Voltage'] = float(data.get('Voltage_AC_Phase_3', 0))
      #self._acloaddbusservice['/Ac/L2/Current'] = float(data.get('Current_AC_Phase_2', 0))
      #self._acloaddbusservice['/Ac/L3/Current'] = float(data.get('Current_AC_Phase_3', 0))
      #self._acloaddbusservice['/Ac/L2/Power'] = -float(data.get('PowerReal_P_Phase_2', 0))
      #self._acloaddbusservice['/Ac/L3/Power'] = -float(data.get('PowerReal_P_Phase_3', 0))
      #self._acloaddbusservice['/Ac/L2/Energy/Forward'] = 0
      #self._acloaddbusservice['/Ac/L2/Energy/Reverse'] = 0
      #self._acloaddbusservice['/Ac/L3/Energy/Forward'] = 0
      #self._acloaddbusservice['/Ac/L3/Energy/Reverse'] = 0

    fronius_pv = float(site_data.get('P_PV', 0))
    virtual_grid = MeterConsumption - fronius_pv
    self._gridbusservice['/Ac/Power'] = virtual_grid

    logging.info("Grid Consumption: %s" % (virtual_grid))
    return True

  def _handlechangedvalue(self, path, value):
    logging.debug("someone else updated %s to %s" % (path, value))
    return True # accept the change

def main():
  logging.basicConfig(level=logging.INFO)
  thread.daemon = True # allow the program to quit

  from dbus.mainloop.glib import DBusGMainLoop
  # Have a mainloop, so we can send/receive asynchronous calls to and from dbus
  DBusGMainLoop(set_as_default=True)

  pvac_output = DbusDummyService(
    servicename='com.victronenergy.grid.'+cfg.fronius_pvinverter["name"],
    deviceinstance=40,
    paths={
      '/ErrorCode': {'initial': 0},
      '/Ac/Power': {'initial': 0},
      '/Ac/Current': {'initial': 0},
      '/Ac/Energy/Forward': {'initial': 0}, # energy bought from the grid
      '/Ac/Energy/Reverse': {'initial': 0}, # energy sold to the grid
      '/Ac/L1/Voltage': {'initial': 0},
      '/Ac/L2/Voltage': {'initial': 0},
      '/Ac/L3/Voltage': {'initial': 0},
      '/Ac/L1/Current': {'initial': 0},
      '/Ac/L2/Current': {'initial': 0},
      '/Ac/L3/Current': {'initial': 0},
      '/Ac/L1/Power': {'initial': 0},
      '/Ac/L2/Power': {'initial': 0},
      '/Ac/L3/Power': {'initial': 0},
      '/Ac/L1/Energy/Forward': {'initial': 0},
      '/Ac/L1/Energy/Reverse': {'initial': 0},
      '/Ac/L2/Energy/Forward': {'initial': 0},
      '/Ac/L2/Energy/Reverse': {'initial': 0},
      '/Ac/L3/Energy/Forward': {'initial': 0},
      '/Ac/L3/Energy/Reverse': {'initial': 0},
    })

  logging.info('Connected to DBUS, and switching over to gobject.MainLoop() (= event based)')
  mainloop = GLib.MainLoop()
  mainloop.run()

if __name__ == "__main__":
  main()

