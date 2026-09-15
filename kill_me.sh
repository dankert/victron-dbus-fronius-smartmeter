#!/bin/bash
kill $(pgrep -f 'python /data/dbus-fronius-smartmeter/dbus-fronius-smartmeter-acload.py')
kill $(pgrep -f 'python /data/dbus-fronius-smartmeter/dbus-fronius-smartmeter-grid.py')
