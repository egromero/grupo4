#!/usr/bin/env python
import rospy
import numpy as np
import cv2

from std_msgs.msg import Bool,String
from parameters import *
from gridmap import *

class State( object ):

  def __init__( self, node_id, pixmap, cell_size = (7, 7) ):
    self.node_id = node_id      # Current cell coordinate (x, y)
    self.pixmap = pixmap        # Map image. For example, in ROS format (-1: unknown, 0: free, 100: busy)
    self.cell_size = cell_size  # Cell size in pixels ( without walls )
    self.prev_action = None     # Action to get this state. Initial state must have a None value.
    self.parent = None          # Previous state

  # IMPLEMENT ME!
  def expand( self ):   # State( pos, map )
    successors = list()
    # Step 1: Convert from the cell's coordinate (x, y) to the cell's central pixel of map image (x_pix, y_pix).
    center = grid_center(self.node_id)

    # Step 2: Determine whether exist a wall between the current cell's central pixel and the adjacent cell's
    #         central pixel, based on the pixel's values between centers.
    neighbours = get_neighbour(center)
    for n in neighbours.keys():
        if neighbours[n]:
            wall = check_wall(self.pixmap, center, neighbours[n])

            # Step 3: If there is not a wall, create the successor state and add it to the 'successors' list.
            #         Consider the following action definition: 'go_north', 'go_south', 'go_east', 'go_west'
            if not wall:
                new = State(neighbours[n], self.pixmap)
                new.prev_action = n
                new.parent = self
                successors.append(new)

    return successors

  def __eq__( self, other ):
    if isinstance(other, State):
      return self.node_id == other.node_id
    else:
      return False

  def __hash__( self ):
    return hash( self.node_id )

  def __str__( self ):
    return str( self.node_id )


def bf_search( s0, sg ):
    open_queue = list()
    closed_queue = list()
    open_queue.append( s0 )
    while len( open_queue ) > 0:
        s = open_queue.pop( 0 )
        closed_queue.append( s )
        if s.node_id == sg.node_id:
            break
        successors = s.expand()
        successors = list( set( successors ) - set( open_queue ) - set( closed_queue ) )
        open_queue += successors
    return s

def get_sequence( sg ):
  aseq = list()
  s = sg
  while None != s.parent: # Is this state the initial state
    aseq.append( ( s.parent.node_id, s.prev_action, s.node_id ) )
    s = s.parent
  return aseq[::-1] # Invert sequence order from sg->...->s0 to s0->...->sg

def img2map( pixvalue, occupied_thresh, free_thresh ):
  p = (255 - pixvalue) / 255.0
  if p > occupied_thresh:
    return 100
  elif p < free_thresh:
    return 0
  else:
    return -1


class Camino():
    def __init__(self):
        self.inicio, self.fin = None, None

        self.path_pub = rospy.Publisher('path_to_point',String,queue_size=10)
        rospy.Subscriber('move_to',String,self.get_path)

    def get_path(self, data):
        self.inicio, self.fin = json.loads(data.data)
        puntos = self.func(map_name, self.inicio, self.fin)
        encoded = json.dumps(puntos)
	self.path_pub.publish(encoded)

    def func(self, map, cell_s, cell_g):
     
        map_img = cv2.imread( map, cv2.IMREAD_GRAYSCALE )
        vect_img2map = np.vectorize( img2map )
        ros_map = vect_img2map( map_img, 0.65, 0.196 )

        cell_s, cell_g = grid_center(cell_s), grid_center(cell_g)

        s0 = State( cell_s, ros_map ) 
        sg = State( cell_g, ros_map ) 


        sg = bf_search( s0, sg ) 
        result = get_sequence( sg )

       
        return [cell_b for cell_a, action, cell_b in result]

if __name__ == '__main__':
    rospy.init_node('path_maker')
    path_maker = ()
    rospy.spin()	
