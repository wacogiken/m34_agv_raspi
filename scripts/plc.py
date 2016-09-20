#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import rospy
import ast
from m34_agv_raspi.msg import plc_msgs
from threading import Thread, BoundedSemaphore
from time import sleep

class plcManager:
    def __init__(self):
        rospy.init_node('plc_node', anonymous=False)
        rospy.on_shutdown(self.shutdown)

        self.pub = rospy.Publisher('plc', plc_msgs, queue_size=1)

        port_name = rospy.get_param('~serial_ports/port_name', '/dev/plc')
        port_baud = rospy.get_param('~serial_ports/baud_rate', 115200)
        self.ser = serial.Serial(port_name, port_baud, timeout=0.01)
	self.ser.flush()
	self.ser.flushInput()
	self.ser.flushOutput()
        
	self.loop()
        
    def shutdown(self):
        self.ser.close()

    def loop(self):
	plc = plc_msgs()
        while not rospy.is_shutdown():
            s = self.recv()
	    if len(s) == 7:
		plc.flag = bool(int(s[0]))
		plc.adrs = int(s[1:3])
		plc.pote = int(s[3:7])
		self.pub.publish(plc)
		if plc.flag:
		    sleep(1)
		    rospy.signal_shutdown('')

    def recv(self):
        s = ''
        loopf = True
        while loopf:
            c = self.ser.read()
            if (len(c) == 0):
		sleep(0.01)
            else:
                if c == chr(0x02):
                    s=''
                elif c == chr(0x03):
        	    print '[', s, ']'
                    sum=0
                    for i in s[:-2]:
                        sum += ord(i)
                        chk = ast.literal_eval('0x'+s[-2:])
                        if (sum & 0xff) == chk:
                            loopf = False
                else:
                    s += c

        #print '[', s, ']'

        return s[:len(s)-2]

if __name__ == '__main__':
    try:
        semaphore = BoundedSemaphore(1)
        manager = plcManager()
    except rospy.ROSInterruptException:
            pass

