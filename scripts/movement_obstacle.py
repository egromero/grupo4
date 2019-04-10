# A very basic TurtleBot script that moves TurtleBot forward indefinitely. Press CTRL + C to stop.  To run:
# Requirements:
# Turtlebot: roslaunch turtlebot_bringup minimal.launch
# Kinect:    roslaunch openni_launch openni.launch
# Sound:     roslaunch sound_play soundplay_node.launch

import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import numpy as np
import time
import os


correction_fact = 0

item_list = [[1,0],[1,1],[0,1],[0,0]]*3
print(item_list)
file_number = 1

center = [240,320]
window = [100,80]
threshold = [0.1,0.7]


dir_path = os.path.dirname(os.path.realpath(__file__))
read_file = dir_path + '/number.txt'
with open(read_file) as file:
    file_number = int(file.readline().rstrip('\n'))
print(file_number)
with open(read_file,'w') as file:
    file.write(str(file_number+1))
filename = '/data' + str(file_number) + '.txt'



real_vel = 0.46
def pi_fix(angle_in):
    if angle_in<-np.pi:
        sub = angle_in+2*np.pi
    elif angle_in>np.pi:
        sub = angle_in-2*np.pi
    else:
        sub = angle_in
    return sub

class GoForward( object ):

    def __init__( self ):
      # tell user how to stop TurtleBot
      rospy.loginfo( "To stop TurtleBot CTRL+C" )
      self.write = True
      self.ref = True
      self.obstacle = False
      self.zero = [0,0,0,0]
      rospy.Subscriber( 'odom', Odometry, self.Position)
      if self.write:
          self.file = open(dir_path+filename,'w')
          self.file.write('starting new something.\n')
          self.flag = 0
      # What method to call when you ctrl + c
      rospy.on_shutdown( self.shutdown )

      # Create a publisher which can "talk" to TurtleBot and tell it to move
      # Tip: You may need to change cmd_vel_mux/input/navi to /cmd_vel if you're not using TurtleBot2
      self.cmd_vel = rospy.Publisher( '/cmd_vel_mux/input/navi', Twist, queue_size=10 )
      self.__depth_img = rospy.Subscriber( '/camera/depth/image', Image ,self.__depth_handler )


      # TurtleBot will stop if we don't keep telling it to move.  How often should we tell it to move? 10 HZ
      self.r = rospy.Rate( 10 );

      # Twist is a datatype for velocity
      self.move_cmd = Twist()
      self.pos = [0 for x in xrange(3)]
      self.ang = 0

def __depth_handler( self, data ):
    try:

        ## Get image and delete nans
        #print('in')
        self.current_cv_depth_image = np.nan_to_num(np.asarray( self.bridge.imgmsg_to_cv2( data, "32FC1" )))
        sub_image = self.current_cv_depth_image[center[0]-windows[0] : center[0]+windows[0], center[1]-windows[1] :
        center[1]+windows[1]]
        #np.save(filename,self.current_cv_depth_image)

        one_item = (np.greater(sub_image,threshold[0]) * np.less(sub_image ,threshold[1])).any()
        all_item = (sub_image==0).all()
        self.obstacle = True if (one_item and all_item) else False
        ## Check if theres anss obstacle in your face


        #print('showing')
        #cv2.imshow('depht',np.nan_to_num(self.current_cv_depth_image))
        #cv2.waitKey(0)
        #print('closed')
    except Exception as e:
        print('error')
        rospy.logerr( e )


    def aplicar_velocidad(self, vel_lineal, vel_angular, time):
       vel_lineal, vel_angular, time = iter(vel_lineal), iter(vel_angular), iter(time)
       current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))
       while current_action[2]:
           print(current_action)
           self.file.write('Nueva rutina: {}\n'.format(current_action))
           now = rospy.Time.now().to_sec()
           current_time = 0
           ref = 0
           while (current_time < current_action[2]+0.2) and not rospy.is_shutdown():
               if not self.obstacle:
                   self.move(current_action[0], current_action[1])
                   current_time = rospy.Time.now().to_sec() - now - ref
               else:
                   ref = rospy.Time.now().to_sec() - current_time
                   self.move(0,0)
                   time.sleep(0.2)
               if self.flag ==2:
                   print('Time: {}\n'.format(current_time))
                   self.file.write('Time: {}\n'.format(current_time))
           current_action = (next(vel_lineal, None), next(vel_angular,None), next(time, None))


       self.move(0,0)
    def mover_robot_goal_beta(self,pos):
        ## Debug print
        #print(self.pos[0])
        #print(self.pos[1])
        #print(pos[0])
        #print(pos[1])

        ## since division by 0 is not allowed, gotta improvise. FIX
        if abs((pos[0]-self.pos[0]))<0.00000000001:
            dif = 0.000000000001
        else:
            dif = pos[0]-self.pos[0]

        ##  Absolute angle of target
        aim_angle = np.arctan((pos[1]-self.pos[1])/dif)
        if dif<0:
            aim_angle = pi_fix(aim_angle+np.pi)

        ## Relative angle of target
        delta_angle = pi_fix(aim_angle - self.ang)
        #print(aim_angle)
        #print(delta_angle)

        ## Distance between target and acutal position
        module =  np.sqrt(np.power((pos[1]-self.pos[1]),2) + np.power((pos[0]-self.pos[0]),2))


        ## Set values with corresponding sign
        angular_speed = 0.8 if delta_angle>0 else -0.8
        real_speed = 0.46 if delta_angle>0 else -0.46
        delta_pos = 0.26 if delta_angle>0 else -0.26
        linear = [0,0.2]
        angular = [angular_speed,0]

        ## the 0.8 and 0.26 values are a kind of a fix.
        angular_time = (delta_angle-delta_pos)/real_speed + 0.8 if (abs(delta_angle)>0.26) else 0.00000001

        time = [angular_time,module/0.2 + 0.000001]
        return linear,angular,time


    def linearecta(self, limit):

        self.flag=2
        for item in item_list:
                vl, va, t = self.mover_robot_goal_beta(item)
                #print(vl)
                #print(va)
                #print(t)
                self.aplicar_velocidad(vl,va,t)
        self.flag=3
        #print('Se termino la segunda rutina')

## meter control bangbang
        return 0

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

        #print(pose)
        if self.ref:
            print('got')
            self.zero[0] = odom_data.pose.pose.position.x
            self.zero[1] = odom_data.pose.pose.position.y
            self.zero[2] = odom_data.pose.pose.position.z
            angaux = odom_data.pose.pose.orientation.w
            self.zero[3] = 2*math.acos( angaux ) if (odom_data.pose.pose.orientation.w < 0) else -2*math.acos( angaux )
            self.ref = False
            #print(self.zero[3])

        self.pos[0] = np.cos(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0]) + np.sin(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1])
        self.pos[1] = np.cos(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1]) - np.sin(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0])
        self.pos[2] = odom_data.pose.pose.position.z  - self.zero[2]
        angaux = odom_data.pose.pose.orientation.w
        angaux2 = -2*math.acos( angaux ) if (odom_data.pose.pose.orientation.z < 0) else 2*math.acos( angaux )
        #print('Angaux2 = {}'.format(angaux2))
        #print('dif = {}'.format(angaux2-self.zero[3]))
        if angaux2-self.zero[3]>math.pi:
            self.ang = (angaux2-self.zero[3])-2*math.pi
        elif angaux2 - self.zero[3] < -math.pi:
            self.ang = (angaux2-self.zero[3]) + 2*math.pi
        else:
            self.ang  = angaux2 - self.zero[3]
        #print(self.ang)
        #print(self.pos[0])
        if self.flag == 2:
            self.file.write('X:{}, Y:{}, Z:{}, Angle:{}\n'.format(self.pos[0],self.pos[1],self.pos[2],self.ang))
            #print('X:{}, Y:{}, Z:{}, Angle:{}\n'.format(self.pos[0],self.pos[1],self.pos[2],self.ang))
        if self.flag == 3:
            self.file.close()
            self.flag = 4
            print('Se cerro archivo')




    def shutdown( self ):
      # stop turtlebot
      rospy.loginfo( "Stopping TurtleBot" )
      # a default Twist has linear.x of 0 and angular.z of 0.  So it'll stop TurtleBot
      self.cmd_vel.publish( Twist() )
      # sleep just makes sure TurtleBot receives the stop command prior to shutting down the script
      rospy.sleep( 1 )
