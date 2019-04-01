#! /usr/bin/env python

import rospy
import math
import roslib
from movement import GoForward
from turtlebot_audio import TurtlebotAudio

from sensor_msgs.msg import Image

import numpy
import cv2
from cv_bridge import CvBridge, CvBridgeError


class TurtlebotTest( object ):

   def __init__( self ):

      self.bridge = CvBridge()

      #self.current_cv_depth_image = numpy.zeros( (1, 1, 3) )
      self.movement = GoForward()
      rospy.sleep(1)
      vl = [0.1,0.2,0,0.1]
      va = [0, 0, 0.8, 0.8]
      t = [1,2,2,1]
      self.movement.aplicar_velocidad(vl,va,t)
      while math.degrees(self.movement.ang)< 90:
          print(math.degrees(self.movement.ang))
          self.movement.move(0,0.8)
      #self.speaker = TurtlebotAudio()
      #self.currAction = None
      #self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image , self.__depth_handler )

   def __depth_handler( self, data ):
      try:
         self.current_cv_depth_image = numpy.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" ) )
         self.explore()
      except CvBridgeError, e:
         rospy.logerr( e )

   def explore( self ):
      lineas = [self.current_cv_depth_image[x,0:540] for x in [10,250,470]]
      minlinea = self.calcmin( lineas )
      if minlinea > 0.6:
         if self.currAction is not 'going forward':
            self.movement.move( 0, 0 )
            self.speaker.say( 'going forward' )
            self.currAction = 'going forward'
            rospy.sleep( 1 )
         self.movement.move( min( 0.3, (minlinea-0.5) ), 0 )
      else:
         if self.currAction is not 'rotating':
            self.movement.move( 0, 0 )
            self.speaker.say( 'rotating' )
            self.currAction = 'rotating'
            rospy.sleep( 1 )
         self.movement.move( 0, 1.2 )
      rospy.loginfo( minlinea )

   def calcmin( self, lineas ):
      minlinea = 100
      for linea in lineas:
         for valor in linea:
            if valor > 0.4 and valor < minlinea:
               minlinea = valor
      return minlinea


if __name__ == '__main__':

   rospy.init_node( "turtlebot_test" )
   handler = TurtlebotTest()
   rospy.spin()
