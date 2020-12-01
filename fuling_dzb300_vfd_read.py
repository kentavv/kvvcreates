#!/usr/bin/env python

# Copyright 2020 Kent A. Vander Velden <kent.vandervelden@gmail.com>
#
# If you use this software, please consider contacting me. I'd like to hear
# about your work.
#
# This file is part of fuling_dzb300_vfd_read.py and tested on a Fuling
# DZB312B002.2L2DK VFD. May work with any Fuling DZB200 and DZB300 VFD.
#
#     DMM-Dyn4 is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     DMM-DYN4 is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of

from __future__ import print_function

import serial
import sys
import time
import random

from pymodbus.client.sync import ModbusSerialClient as ModbusClient

import hal, time

use_linuxcnc = True
log_fn = 'fuling.log'

# This is the serial number of the RS485 device. The serial number can be
# found using a combination of 
#   sudo dmesg
# and
#   sudo lsusb -v | egrep -n 'idVendor|idProduct|iManufacturer|iProduct|iSerial|^Bus'
# after attaching the device.
f_serial_number = 'AL05ZQ8W'


def read_parameters(client, unit):
  for i in range(149):
    if i == 78:
        # Reading the password register will cause an error
        continue

    addr = i
    # Can read up to 16 registers at once
    # rr = client.read_holding_registers(addr, 16, unit=unit)
    rr = client.read_holding_registers(addr, 1, unit=unit)
    if rr.isError():
        row = i, '(error)'
    else:
        row = i, rr.registers[0]
    print('{} {}'.format(*row))
    # Some delay is needed in this fast loop else many errors occur
    # 8ms seems to be the minimum
    time.sleep(.010)


def read_status(client, unit):
    def h(s, n):
        time.sleep(.01)
        rr = client.read_holding_registers(s, n, unit=unit)
        if rr.isError():
          return ['-'] * n
        else:
          return rr.registers

    lst = []
    lst.extend(h(0x1000, 1))
    lst.extend(h(0x1001, 1))
    lst.extend(h(0x2000, 1))
    lst.extend(h(0x3000, 16))
    lst.extend(h(0x3010, 3))
    lst.extend(h(0x5000, 1))
    lst.extend(h(0x5001, 1))

    return lst


def read_op_status(client, unit):
    def h(s, n):
        time.sleep(.01)
        rr = client.read_holding_registers(s, n, unit=unit)
        if rr.isError():
          return ['-'] * n
        else:
          return rr.registers

    d = {'time': time.time()}

    # TODO Consider reading current op less frequently to prioritize 
    #  reading of the status (0x3000)
    d['op'] = h(0x1001, 1)[0]

    # Only read the fault explanation if there is a fault
    if d['op'] == 0x4:
        d['fault'] = h(0x5000, 1)[0]
    else:
        d['fault'] = ''

    # Don't read the trailing unused registers
    lst = h(0x3000, 8)

    d['setting_frequency'] = lst[0]
    d['running_frequency'] = lst[1]
    d['output_current'] = lst[2]
    d['output_voltage'] = lst[3]
    d['running_speed'] = lst[4]
    d['output_power'] = lst[5]
    d['output_torque'] = lst[6]
    d['dc_bus_voltage'] = lst[7]
    # d['pid_setpoint'] = lst[8]
    # d['pid_feedback'] = lst[9]
    # d['input_terminal_status'] = lst[10]
    # d['output_terminal_status'] = lst[11]
    # d['vi_value'] = lst[12]
    # d['ci_value'] = lst[13]
    # d['current_segment_of_multi-speed_control'] = lst[14]
    # d['reserved1'] = lst[15]

    return d


def find_device():
    devs = []

    global serial
    if serial.VERSION > '2.5':
        import serial.tools.list_ports

        for dev in serial.tools.list_ports.comports():
            # 'apply_usb_info', 'description', 'device', 'device_path', 'hwid', 'interface', 'location', 'manufacturer', 'name', 'pid', 'product', 'read_line', 'serial_number', 'subsystem', 'usb_description', 'usb_device_path', 'usb_info', 'usb_interface_path', 'vid'
            # print(dev, dev.manufacturer, dev.product, dev.device, dev.serial_number)
            # if dev.description == 'FT230X Basic UART' and dev.manufacturer == 'FTDI' and dev.product == 'FT230X Basic UART':
            # if dev.manufacturer == 'FTDI' and dev.product == 'FT230X Basic UART':
            # if dev.manufacturer == 'FTDI' and dev.product == 'FT232R USB UART':
            if dev.manufacturer == 'FTDI' and dev.serial_number == f_serial_number:
                devs += [dev.device]
    else:
        # LinuxCNC 2.7.15 is still tied to Python2
        import glob
        devs = glob.glob('/dev/ttyUSB*')

    if not devs:
        print('No known serial devices found.')
        return ''

    if len(devs) > 1:
        print('More than one serial devices found...')
        for dev in devs:
            print(dev)
        print('Selecting first serial device.')

    print('Using device at:', devs[0])
    return devs[0]


def serial_loop(client, h):
    unit = 0x1

    header = ['time', 'output_power', 'setting_frequency', 'fault', 'running_frequency', 'running_speed', 'dc_bus_voltage', 'output_torque', 'output_voltage', 'output_current', 'op']

    with open(log_fn, 'a') as f:
        s = ','.join(header)
        # print(s)
        print(s, file=f)

        while True:
            d = read_op_status(client, unit)
            try:
                h['power'] = float(d['output_power'])
                h['bus_voltage'] = float(d['dc_bus_voltage']) / 10.
                h['current'] = float(d['output_current']) / 10.
                h['torque'] = float(d['output_torque'])
                h['voltage'] = float(d['output_voltage'])
            except ValueError:
                print('Unable to convert', d)
                h['power'] = -1
                h['bus_voltage'] = -1
                h['current'] = -1
                h['torque'] = -1
                h['voltage'] = -1

            s = ','.join([str(d[k]) for k in header])
            # print(s)
            print(s, file=f)


def main():
    if use_linuxcnc:
        h = hal.component("fuling")
        h.newpin("in", hal.HAL_FLOAT, hal.HAL_IN)
        h.newpin("enable", hal.HAL_BIT, hal.HAL_IN)
        h.newpin("logen", hal.HAL_BIT, hal.HAL_IN)
        h.newpin("power", hal.HAL_FLOAT, hal.HAL_OUT)
        h.newpin("bus_voltage", hal.HAL_FLOAT, hal.HAL_OUT)
        h.newpin("current", hal.HAL_FLOAT, hal.HAL_OUT)
        h.newpin("torque", hal.HAL_FLOAT, hal.HAL_OUT)
        h.newpin("voltage", hal.HAL_FLOAT, hal.HAL_OUT)
        h.ready()
    else:
        h = { 'in': 0.,
              'enable': True,
              'logen': True,
              'power': 0.,
              'bus_voltage': 0.,
              'current': 0.,
              'torque': 0.,
              'voltage': 0. }

    try:
        while True:
            dev_fn = find_device()
            if dev_fn:
#                try:
                    client = ModbusClient(method='rtu', port=dev_fn, timeout=1, baudrate=38400)
                    client.connect()

                    serial_loop(client, h)
#                except DMMTimeout:
#                    print('Timedout')
#                    # raise
#                except serial.serialutil.SerialException as e:
#                    # SerialException: could not open port /dev/ttyUSB1: [Errno 2] No such file or directory: '/dev/ttyUSB1'
#                    # SerialException: device reports readiness to read but returned no data (device disconnected?)
#                    print('SerialException:', e)
            print('Kicked out... resting before retrying.')
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    #for i in [0x1000, 0x1001, 0x2000,
    #          0x3000, 0x3001, 0x3002, 0x3003,
    #          0x3004, 0x3005, 0x3006, 0x3007,
    #          0x3008, 0x3009, 0x300A, 0x300B,
    #          0x300C, 0x300D, 0x300E, 0x300F,
    #          0x3010, 0x3011, 0x3012,
    #          0x5000, 0x5001]:
    #    addr = i
    #    rr = client.read_holding_registers(addr, 1, unit=UNIT)
    #    if rr.isError():
    #        print(i, False, '---')
    #    else:
    #        print(i, True, rr.registers)
    #    time.sleep(.01)

    #lst = {'control command': [0x1000, 0, 0],
    #'inverter state': [0x1001, 0, 0],
    #'': [0x1001, 0, 0],
    #'': [0x1001, 0, 0],

    # read_parameters(client, unit)
    # read_status(client, unit)


if __name__ == "__main__":
    main()
