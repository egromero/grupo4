import rospy
import roslib

class TurtlebotTest( object ):
   def __init__( self ):
       pass

   def aplicar_velocidad(self, vel_lineal, vel_angular, time):

       now = rospy.get_time().to_sec()
       print(now)
       current_time = 0
       while current_time < time:
           self.move(vel_lineal,vel_angular)
           current_time = rospy.get_time().to_sec() - now

  def move( self, vel, ang ):
     self.move_cmd.linear.x = vel
     self.move_cmd.angular.z = ang
     # publish the velocity
     self.cmd_vel.publish( self.move_cmd )
     self.r.sleep()


if __name__ == '__main__':
    rospy.init_node( "turtlebot_test" )
    handler = TurtlebotTest()
    rospy.spin()
