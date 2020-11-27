#!/usr/bin/python

fn = '/dev/ttyUSB1'

import time
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

client = ModbusClient(method='rtu', port='/dev/ttyUSB1', timeout=1, baudrate=38400)

client.connect()

UNIT = 0x1
#lst = {'control command': [0x1000, 0, 0],
#'inverter state': [0x1001, 0, 0],
#'': [0x1001, 0, 0],
#'': [0x1001, 0, 0],

def read_parameters():
  for i in range(149):
    if i == 78:
        # Not able to read the password register
        continue

    addr = i
    # Can read up to 16 registers at once
    # rr = client.read_holding_registers(addr, 16, unit=UNIT)
    rr = client.read_holding_registers(addr, 1, unit=UNIT)
    if rr.isError():
        print(i, False, '---')
    else:
        print(i, True, rr.registers)
    # Some delay is needed in this fast loop else many errors occur
    # 8ms seems to be the minimum
    time.sleep(.010)

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

#read_parameters()

def read_status():
  i = 0


  def h(s, n):
    time.sleep(.01)
    rr = client.read_holding_registers(s, n, unit=UNIT)
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

def read_op_status():
  i = 0


  def h(s, n):
    time.sleep(.01)
    rr = client.read_holding_registers(s, n, unit=UNIT)
    if rr.isError():
      return ['-'] * n
    else:
      return rr.registers

  d = {}

  lst = h(0x1001, 1)
  d['op'] = lst[0]

  if d['op'] == 0x4:
      lst = h(0x5000, 1)
      d['fault'] = lst[0]

  lst = h(0x3000, 15)
  d['setting_frequency'] = lst[0]
  d['running_frequency'] = lst[1]
  d['output_current'] = lst[2]
  d['output_voltage'] = lst[3]
  d['running_speed'] = lst[4]
  d['output_power'] = lst[5]
  d['output_torque'] = lst[6]
  d['dc_bus_voltage'] = lst[7]
#  d['pid_setpoint'] = lst[8]
#  d['pid_feedback'] = lst[9]
#  d['input_terminal_status'] = lst[10]
#  d['output_terminal_status'] = lst[11]
  d['vi_value'] = lst[12]
#  d['ci_value'] = lst[13]
#  d['current_segment_of_multi-speed_control'] = lst[14]

  return d

while True:
    lst = read_op_status()
    print(time.time(), lst)

