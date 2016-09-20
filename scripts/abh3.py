#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pkflt
import serial
import rospy
import ast
from m34_agv_raspi.msg import abh3_msgs
from m34_agv_raspi.msg import abh3_diag
from threading import Thread, BoundedSemaphore
#from time import sleep
from m34_agv_raspi.msg import plc_msgs

abh3_header = 'FFFF'

diag_cmd  = ('CM1054', 'CM1064', 'CM1012', 'CM1022', 'CM1031', 'CM1041', 'CM103B', 'CM104B', 'CM1004', 'CM1005', 'CM0003', 'CM0005', 'CM0001', 'CM0000')
diag_pkflt = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0]
diag_value = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
diag_num = 14

class abh3Manager:
    def __init__(self):
        rospy.init_node('abh3_node', anonymous=False)
        rospy.on_shutdown(self.shutdown)

        driver_item = rospy.get_param('~driver_item', 'abh3')
        driver_name = rospy.get_param('~driver_name', 'no1')

        self.pub = rospy.Publisher('/%s/%s/out' % (driver_item, driver_name), abh3_msgs, queue_size=1)
        self.plc = rospy.Subscriber('plc', plc_msgs, self.plc_handler)

        port_name = rospy.get_param('~serial_ports/port_name', '/dev/abh3')
        port_baud = rospy.get_param('~serial_ports/baud_rate', 115200)
        self.ser = serial.Serial(port_name, port_baud, timeout=5)
	self.ser.flush()
	self.ser.flushInput()
	self.ser.flushOutput()
        self.semaphore = semaphore
        
        self.diag_rate = rospy.get_param('~serial_ports/diag_rate', 100)
        self.diag_pub = rospy.Publisher('/%s/%s/diag' % (driver_item, driver_name), abh3_diag, queue_size=1)
        if self.diag_rate > 0:
            Thread(target=self.diag).start()
        
    def shutdown(self):
        self.ser.close()

    def diag(self):
        rate = rospy.Rate(self.diag_rate)
        i = 0
        diag_sts = abh3_diag()

        while not rospy.is_shutdown():
            for i in range(len(diag_value)):
                self.semaphore.acquire()
                cmd = abh3_header + diag_cmd[i]
                flag, ret = self.trans(cmd)
                self.semaphore.release()
                if flag:
                    j = int(ret, 16)
                    if diag_pkflt[i] == 1:
                        diag_value[i] = pkflt.pkflt_to_flt(j)
                    else:
                        if j > 2147483647:
                            j -= 4294967296
                        diag_value[i] = j
    
            	diag_sts.posAY, diag_sts.posBX, \
            	diag_sts.velAY, diag_sts.velBX, \
            	diag_sts.trqAY, diag_sts.trqBX, \
            	diag_sts.loadAY, diag_sts.loadBX, \
            	diag_sts.voltM, diag_sts.voltC, \
            	diag_sts.inp, diag_sts.outp, \
            	diag_sts.warn, diag_sts.alarm = diag_value
    
            	self.diag_pub.publish(diag_sts)
                rate.sleep()

    def trans(self, command, flag=True):
        i=0
        for t in command:
            i = i+ord(t)
        t=hex(65536-i)
        s = chr(0x02)+command+t[len(t)-2:].upper()+chr(0x03)
        self.ser.write(chr(0x02)+command+t[len(t)-2:].upper()+chr(0x03))
        s = ''
        loopf = True
        while loopf:
            c = self.ser.read()
            if (len(c) == 0):
                s = ''
                loopf = False
            else:
                if c == chr(0x02):
                    s=''
                elif c == chr(0x03):
                    loopf = False
                else:
                    s += c

        if s == '':
            return [False, s]
        else:
            sum = 0
            for i in s[:-2]:
                sum += ord(i)
            chk = ast.literal_eval('0x' + s[-2:])
            if (sum + chk) & 0xff == 0:
                if flag == False:
                    return [True, s[:len(s)-2]]
                else:
                    if s[4] == chr(0x15):
                        return [False, s[5:len(s)-2]]
                    else:
                        return [True, s[5:len(s)-2]]
            else:
                return [False, s]

    def plc_handler(self, plc):
	if plc.flag:
	    rospy.signal_shutdown('')

if __name__ == '__main__':
    try:
        semaphore = BoundedSemaphore(1)
        manager = abh3Manager()
        rospy.spin()
    except rospy.ROSInterruptException:
            pass

