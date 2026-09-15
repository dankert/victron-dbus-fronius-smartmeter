#!/usr/bin/env python

fronius_smartmeter = {
    "ipaddress": "###IPADDRESS###",     # IPv4 Address or hostname of AC Smart Meter
    "numphases": 3,     # Count of phases of the smartmeter, can be 1 or 3
    "name": "fronius_smartmeter",
    "interval": 2000, # poll interval
}

fronius_pvinverter = {
    "ipaddress": "###IPADDRESS###",     # IPv4 Address or hostname of Fronius PV inverter
    "name": "fronius_virtual_grid_meter",
}
