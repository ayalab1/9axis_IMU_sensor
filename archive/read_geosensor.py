#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Very simple example code to read data from a 9Dof inertial measurement unit (IMU) sensor.

@author: hongyu chang
"""

from __future__ import print_function

#import click
import serial
import time
import os.path as op
import os
import numpy as np
import threading
from collections import deque
import traceback
import struct
import csv


class WriteThread(threading.Thread):

    def __init__(self, output):

        assert output is not None

        super(WriteThread, self).__init__()

        if isinstance(output, str):

            output = op.expanduser(output)

            if op.isdir(output):
                # directory
                if not op.exists(output):
                     os.makedirs(output)
                of = op.join(output, 'imu_data3.csv')
            else:
                # file
                output_dir = op.split(output)[0]
                if not op.exists(output_dir):
                    os.makedirs(output_dir)
                of = output
        else:
            # stream etc
            of = output

        self.output = output
        self.file = of
        self.lock = threading.Lock()
        self.should_exit = False
        self.data = deque()
    def append(self, x):

        with self.lock:
            self.data.append(x)

    def stop(self):

        with self.lock:
            self.should_exit = True

    def run(self):
        with open(self.file, 'a') as f:
                line = None
                with self.lock:
                    if len(self.data) > 0:
                        line = self.data.popleft()

                if line is not None:
                    f.write(','.join([str(x) for x in line]) + '\n')
                else:
                    time.sleep(.01)





# @click.command()
# @click.option('--device', '-d', default='COM8')
# @click.option('--baudrate', '-b', default=115200)
# @click.option('--output', '-o', default=r'D:\Documents\GitHub\R_Project\PPP\codebook')
# @click.option('--print-to-terminal', '-t', is_flag=True)
# @click.option('--skip-lines', '-S', is_flag=True)
# @click.option('--sync-signal', '-s', is_flag=True)


def convert_readbytes(record):
    readline=[]
    counts= str(struct.unpack('L',record[52:56])[0])
    readline.append(counts)
    ts=str(struct.unpack('L',record[48:52])[0])
    readline.append(ts)
    accx = str(round(struct.unpack('f',record[:4])[0],7))
    readline.append(accx)
    accy = str(round(struct.unpack('f',record[4:8])[0],7))
    readline.append(accy)
    accz = str(round(struct.unpack('f',record[8:12])[0],7))
    readline.append(accz)
    geox = str(round(struct.unpack('f',record[12:16])[0],7))
    readline.append(geox)
    geoy = str(round(struct.unpack('f',record[16:20])[0],7))
    readline.append(geoy)
    geoz= str(round(struct.unpack('f',record[20:24])[0],7))
    readline.append(geoz)
    magx= str(round(struct.unpack('f',record[24:28])[0],7))
    readline.append(magx)
    magy= str(round(struct.unpack('f',record[28:32])[0],7))
    readline.append(magy)
    magz= str(round(struct.unpack('f',record[32:36])[0],7))
    readline.append(magz)
    Roll= str(round(struct.unpack('f',record[36:40])[0],7))
    readline.append(Roll)
    Yaw= str(round(struct.unpack('f',record[40:44])[0],7))
    readline.append(Yaw)
    Pitch= str(round(struct.unpack('f',record[44:48])[0],7))
    readline.append(Pitch)

    return readline
def cli(ser, output, print_to_terminal, skip_lines,sync_signal):

        write_thread = WriteThread(output)
        write_thread.start()
        time.sleep(.1)
        t0 = time.time()
        counter = 0
        #ser.reset_input_buffer()
        time.sleep(4)
        while True:
            try:
                ser.write(b'h')
                while ser.inWaiting() < 56:
                    pass
                line = ser.read(56)
                    # each line starts with a ">" and ends with a "<"
                    # as openframeworks serial used in the open-ephys
                    # GUI does not have a proper readline function.
                    # we don't need it here so we can ignore them.

                        # values contains:
                        # status, index, ts, ax, ay, az, gx, gy, gz, mx, my, mz
                        # however, we will throw away the index and status
                        # values
                readline=convert_readbytes(line)
                write_thread.append(readline[:])
                write_thread.run()
                counter += 1
                if print_to_terminal:
                    if  not skip_lines or (counter % 5 == 0):
                            print(*readline, sep = ", ",end="\n")



                if counter % 200 == 0:
                    # this should show the frame rate every 1-2 seconds
                    now = time.time()
                    #print("fps:", 200. / (now - t0))
                    t0 = now

            except KeyboardInterrupt:
                break

            except BaseException:
                # print information about potential problems, e.g., partially transmitted data
                traceback.print_exc()

        # stop data acquisition
        ser.write(b"1\n")

        if write_thread is not None:
            write_thread.stop()
            write_thread.run()


if __name__ == '__main__':


    output=r'C:\Users\Cornell\Desktop\PP'
    device="COM5"
    baudrate=115200
    # ser=serial.Serial( device,baudrate,timeout=1)
    write_thread = WriteThread(output)
    ser=serial.Serial( device,baudrate,timeout=1)
    print('start calibration')
    time.sleep(4)
    #read calibration stuffs
    ser.write(b'c')
    while True:
        try:
            line = ser.readline().strip()
            marker= [str(u) for u in line.split(b",")]
            if len(line) > 0:
                if marker[0][2]=='>':
                   line=line[1:-1]
                   print(line)
                   values = [float(x) for x in line.split(b",")]
                   # print(values)
                   write_thread.append(values[:])
                   write_thread.run()
                   ser.flushInput()
                   ser.flushOutput()
                   break
                else:
                   print(line)
        except KeyboardInterrupt:
            break
    print_to_terminal=True
    skip_lines=False
    sync_signal=True
    #read calibration stuffs
    print("start recording")
    cli(ser, output ,print_to_terminal, skip_lines, sync_signal)

   # line = ser.readline().strip()
    #print("start calibration")
    #
    # write_thread = WriteThread(output)
    # write_thread.start()
    # write_thread.append([1,2,3,4,5])
    # write_thread.run()

    # write_thread = WriteThread(output)
    # write_thread.start()
    # while True:
    #     try:
    #         ser.write(b"4\n")
    #         line = ser.readline().strip()
    #         marker= [str(u) for u in line.split(b",")]
    #         if len(line) > 0:
    #             if marker[0][2]=='>':
    #                line=line[1:-1]
    #                print(line)
    #                values = [float(x) for x in line.split(b",")]
    #                # print(values)
    #                write_thread.append(values[:])
    #                write_thread.run()
    #                break
    #             else:
    #                print(line)

    #     except KeyboardInterrupt:
    #         break
    # write_thread.stop()
    # write_thread.join()
    # print(values)
        #  while ser.inWaiting() < 40:
        #     pass

         #readline=convert_readbytes(line)
         #print(readline)
    # while True:
    #      print('sending info')
    #      ser.write(b'h')
    #      while ser.inWaiting() < 56:
    #            pass
    #      a = ser.read(56)
    #      readline=convert_readbytes(a)
    #      print(readline)
