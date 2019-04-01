# A very basic TurtleBot script that moves TurtleBot forward indefinitely. Press CTRL + C to stop.  To run:
# Requirements:
# Turtlebot: roslaunch turtlebot_bringup minimal.launch
# Kinect:    roslaunch openni_launch openni.launch
# Sound:     roslaunch sound_play soundplay_node.launch

import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry


class GoForward( object ):

   def __init__( self ):
      # tell user how to stop TurtleBot
      rospy.loginfo( "To stop TurtleBot CTRL+C" )

      # What method to call when you ctrl + c
      rospy.on_shutdown( self.shutdown )

      # Create a publisher which can "talk" to TurtleBot and tell it to move
      # Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
      self.cmd_vel = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )

      rospy.Subscriber( 'odom', Odometry, self.Position )

      # TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
      self.r = rospy.Rate( 10 );

      # Twist is a datatype for velocity
      self.move_cmd = Twist()
      self.pos = [0 for x in xrange(3)]
      self.ang = 0

   def aplicar_velocidad(self, vel_lineal, vel_angular, time):
       vel_lineal, vel_angular, time = iter(vel_lineal), iter(vel_angular), iter(time)
       current_action = (next(vel_lineal, None), next(vel_angular), next(time, None))
       while current_action[2]:
           now = rospy.Time.now().to_sec()
           current_time = 0
           while current_time < current_action[2]:
               self.move(current_action[0], current_action[1])
               current_time = rospy.Time.now().to_sec() - now
           current_action = (next(vel_lineal, None), next(vel_angular), next(time, None))

               #print(self.pos, math.degrees(self.ang))
       self.move(0,0)

   def move(self, vel, ang ):
      self.move_cmd.linear.x = vel
      self.move_cmd.angular.z = ang
      # publish the velocity
      self.cmd_vel.publish( self.move_cmd )
      self.r.sleep()

   def linea(self, dist, vel = 0.2 ):
      contvel = vel
      pos2 = [self.pos[0]+dist*math.cos(self.ang), self.pos[1]+dist*math.sin(self.ang)]
      if( dist > 0 ):
         while not rospy.is_shutdown() and (self.pos[0] < pos2[0] or self.pos[1] < pos2[1]):
            print self.pos
            self.moverse(vel-contvel,0)
            if contvel > 0:
               contvel -= vel/5
      else:
         while not rospy.is_shutdown() and (self.pos[0] > pos2[0] or self.pos[1] > pos2[1]):
            self.moverse(-vel+contvel,0)
            if contvel > 0:
               contvel -= vel/5
      self.moverse( 0, 0 )
      rospy.sleep( 0.5 )

   def rotar( self, angu, vel = 0.8 ):
      contvel = vel
      while not rospy.is_shutdown() and self.ang < angu:
         self.moverse( 0, vel-contvel )
         if contvel > 0:
            contvel -= vel/5
         self.moverse( 0, 0 )
         rospy.sleep( 0.5 )

   def Position( self, odom_data ):
      pose = odom_data.pose.pose #  the x,y,z pose and quaternion orientation
      self.pos[0] = odom_data.pose.pose.position.x
      self.pos[1] = odom_data.pose.pose.position.y
      self.pos[2] = odom_data.pose.pose.position.z
      angaux = odom_data.pose.pose.orientation.w
      self.ang = 2 * math.acos( angaux )
      if odom_data.pose.pose.orientation.z < 0:
         self.ang = 2*math.pi - self.ang

   def shutdown( self ):
      # stop turtlebot
      rospy.loginfo( "Stopping TurtleBot" )
      # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
      self.cmd_vel.publish( Twist() )
      # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
      rospy.sleep( 1 )
