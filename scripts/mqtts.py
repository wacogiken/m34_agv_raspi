#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import ast
import paho.mqtt.client as mqtt
from m34_agv_raspi.msg import plc_msgs
from m34_agv_raspi.msg import abh3_diag
from threading import Thread, BoundedSemaphore, Event
from time import sleep, time

class plcManager:
    def __init__(self):
        rospy.init_node('mqtt_node', anonymous=False)
        rospy.on_shutdown(self.shutdown)

        driver_item = rospy.get_param('~driver_item', 'abh3')
        driver_name = rospy.get_param('~driver_name', 'no1')

        self.sub_plc = rospy.Subscriber('/plc', plc_msgs, self.plc_handler)
	self.plc = plc_msgs()
        self.sub_abh3 = rospy.Subscriber('/%s/%s/diag' % (driver_item, driver_name), abh3_diag, self.abh3_handler)
	self.abh3 = abh3_diag()

	self.host = '192.168.250.10'
	self.port = 1883
	self.topic = '/agv'

	self.client = mqtt.Client(protocol = mqtt.MQTTv311)
	self.client.connect(self.host, port=self.port, keepalive=360)

	rospy.spin()

    def shutdown(self):
        self.stop_event.set()

    def plc_handler(self, msg):
	self.plc = msg
	if self.plc.flag:
	    rospy.signal_shutdown('')
    
    def abh3_handler(self, msg):
	self.abh3 = msg
        s = '%.4g:%.4g:%.4g:%d:%d' % (self.abh3.velAY, self.abh3.velBX, self.abh3.voltC, self.plc.adrs, self.plc.pote)
        self.client.publish(self.topic, s)
    
if __name__ == '__main__':
    try:
        semaphore = BoundedSemaphore(1)
        manager = plcManager()
    except rospy.ROSInterruptException:
        manager.shutdown()

