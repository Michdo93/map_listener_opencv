#!/usr/bin/python
import sys
import os
import rospy
from std_msgs.msg import String
from std_msgs.msg import Header
from nav_msgs.msg import OccupancyGrid
from nav_msgs.msg import MapMetaData
from geometry_msgs.msg import Pose
import array
import numpy as np

# OpenCV
import cv2

VERBOSE = False

class MapListener(object):

    def __init__(self):
        """Configure subscriber."""
        # Create a subscriber with appropriate topic, custom message and name of
        # callback function.
        self.sub = rospy.Subscriber("map", OccupancyGrid, self.mapConvert)

        # Initialize message variables.
        self.enable = False

        if self.enable:
            self.start()
        else:
            self.stop()

    def start(self):
        self.enable = True
        self.sub = rospy.Subscriber("map", OccupancyGrid, self.mapConvert)

    def mapConvert(self, msg):
        """Handle subscriber data."""
        header = msg.header

        # declare 1-d array of unsigned char and assign it with values
        buff=array.array('B')

        for i in range(0, msg.info.width*msg.info.height):
            if(msg.data[i] >= 0 and msg.data[i] <= 0):
                buff.append(254)
            elif(msg.data[i] <= 100 and msg.data[i] >= 100):
                buff.append(000)
            else:
                buff.append(205)

        buff = np.array(buff)
        buff = np.reshape(buff, (-1, msg.info.width))

        vis2 = cv2.cvtColor(buff, cv2.COLOR_GRAY2BGR)

        cv2.imshow("/map", vis2)
        cv2.waitKey(25)

    def stop(self):
        """Turn off subscriber."""
        self.enable = False
        self.sub.unregister()


if __name__ == '__main__':
    # Initialize the node and name it.
    node_name = "MapListenerNode"
    rospy.init_node(node_name, anonymous=True)

    mapListener = MapListener()

    # Go to the main loop
    try:
        mapListener.start()
        # Wait for messages on topic, go to callback function when new messages arrive.
        # spin() simply keeps python from exiting until this node is stopped
        rospy.spin()
    # Stop with Ctrl + C
    except KeyboardInterrupt:
        mapListener.stop()

        nodes = os.popen("rosnode list").readlines()
        for i in range(len(nodes)):
            nodes[i] = nodes[i].replace("\n","")

        for node in nodes:
            os.system("rosnode kill " + node_name)


        print("Node stopped")
