#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
from m34_agv_raspi.msg import plc_msgs
from time import sleep, time
from sense_hat import SenseHat
from threading import BoundedSemaphore
from subprocess import call

led_dat = [
    [' ', 270, [255, 255, 255], True ], #  0
    ['A', 180, [255, 255, 255], False], #  1
    [' ', 270, [255, 255, 255], True ], #  2
    ['B', 180, [255, 255, 255], False], #  3
    ['*',   0, [255, 255, 255], False], #  4
    ['C', 180, [255, 255, 255], False], #  5
    [' ', 180, [255, 255, 255], True ], #  6
    ['D', 180, [255, 255, 255], False], #  7
    [' ', 180, [255, 255, 255], True ], #  8
    ['E', 180, [255, 255, 255], False], #  9
    ['*',   0, [255, 255, 255], False], # 10
    ['F', 180, [255, 255, 255], False], # 11
    [' ',  90, [255, 255, 255], True ], # 12
    ['G', 180, [255, 255, 255], False], # 13
    [' ',  90, [255, 255, 255], True ], # 14
    ['H', 180, [255, 255, 255], False], # 15
    ['*',   0, [255, 255, 255], False], # 16
    ['I', 180, [255, 255, 255], False], # 17
    [' ',  90, [255, 255, 255], True ], # 18
    ['J', 180, [255, 255, 255], False], # 19
    [' ',  90, [255, 255, 255], True ], # 20
    ['K', 180, [255, 255, 255], False], # 21
    [' ', 270, [255, 255, 255], True ], # 22
    ['L', 180, [255, 255, 255], False], # 23
    [' ', 270, [255, 255, 255], True ], # 24
    ['M', 180, [255, 255, 255], False], # 25
    [' ', 270, [255, 255, 255], True ], # 26
    ['N', 180, [255, 255, 255], False], # 27
    [' ', 270, [255, 255, 255], True ], # 28
    ['O', 180, [255, 255, 255], False], # 29
    ['*',   0, [255, 255, 255], False], # 30
    ['P', 180, [255, 255, 255], False], # 31
    [' ', 270, [255, 255, 255],  True], # 32
    ['Q', 180, [255, 255, 255], False]  # 33
]

class ledManager:
    def __init__(self):
        rospy.init_node('led_node', anonymous=False)
        rospy.on_shutdown(self.shutdown)

        self.sub_plc = rospy.Subscriber('/plc', plc_msgs, self.plc_handler)
	self.plc = plc_msgs()

	self.sense = SenseHat()
	self.sense.clear()
	self.flag = False

	rate = rospy.Rate(10)
	while not rospy.is_shutdown():
	    if self.plc.flag:
		call("sudo shutdown -h now", shell=True)
		self.sense.show_message('Shutdown', text_colour=[255, 255, 255])
		rospy.signal_shutdown('')
	    else:
	        self.sense.set_rotation(led_dat[self.plc.adrs][1])
	        if led_dat[self.plc.adrs][3]:
		    self.sense.show_message('<-', text_colour=led_dat[self.plc.adrs][2])
	        else:
	            self.sense.show_letter(led_dat[self.plc.adrs][0], text_colour=led_dat[self.plc.adrs][2])
	    rate.sleep()

    def shutdown(self):
	pass

    def plc_handler(self, msg):
	self.plc = msg
	    
    
if __name__ == '__main__':
    try:
	semaphore = BoundedSemaphore(1)
        manager = ledManager()
    except rospy.ROSInterruptException:
        manager.shutdown()

