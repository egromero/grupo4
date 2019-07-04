#! /usr/bin/env python

import rospy
import rospkg
from sound_play.libsoundplay import SoundClient
from std_msgs.msg import Bool
from parameters import *

class TurtleBotAudio():

    def __init__(self):
        rospy.init_node('turtlebot_audio')
        self.sound_client = SoundClient()

        rospack = rospkg.RosPack()
        ws_path = rospack.get_path(pkg_name)
        sound_path = ws_path + "/scripts/" + playfile
	print(sound_path)

        self.sound = self.sound_client.waveSound(sound_path)
	rospy.sleep(2)

        self.play_sub = rospy.Subscriber("music", Bool, self.play_sound_cb)
        print("Subscribing to music")
        while self.play_sub.get_num_connections() < 1 and not rospy.is_shutdown():
            rospy.sleep(0.2)
        print("Subscribed to music")


    def play_sound_cb(self, data):
        if data.data:
            print("Playing sound")
            self.sound.play()

if __name__ == "__main__":
    # rospy.init_node('play_sound_file')
    player = TurtleBotAudio()
    rospy.spin()
