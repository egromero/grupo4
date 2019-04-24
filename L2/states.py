

    def Position( self, odom_data ):
        pose = odom_data.pose.pose #  the x,y,z pose and quaternion orientation

        if self.ref:
            print('got')
            self.zero[0] = odom_data.pose.pose.position.x
            self.zero[1] = odom_data.pose.pose.position.y
            self.zero[2] = odom_data.pose.pose.position.z
            angaux = odom_data.pose.pose.orientation.w
            self.zero[3] = 2*math.acos( angaux ) if (odom_data.pose.pose.orientation.w < 0) else -2*math.acos( angaux )
            self.ref = False
            self.pos[0] = np.cos(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0]) + np.sin(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1])
            self.pos[1] = np.cos(self.zero[3])*(odom_data.pose.pose.position.y-self.zero[1]) - np.sin(self.zero[3])*(odom_data.pose.pose.position.x-self.zero[0])
            self.pos[2] = odom_data.pose.pose.position.z  - self.zero[2]
            angaux = odom_data.pose.pose.orientation.w
            angaux2 = -2*math.acos( angaux ) if (odom_data.pose.pose.orientation.z < 0) else 2*math.acos( angaux )

        if angaux2-self.zero[3]>math.pi:

            self.ang = (angaux2-self.zero[3])-2*math.pi

        elif angaux2 - self.zero[3] < -math.pi:

            self.ang = (angaux2-self.zero[3]) + 2*math.pi
        else:
            self.ang  = angaux2 - self.zero[3]

        if self.flag == 2 and self.write:

            self.file.write('X:{}, Y:{}, Z:{}, Angle:{}\n'.format(self.pos[0],self.pos[1],self.pos[2],self.ang))

        if self.flag == 3 and self.write :
            self.file.close()
            self.flag = 4
            print('Se cerro archivo')
