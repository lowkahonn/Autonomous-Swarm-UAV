#!/usr/bin/env python

import rospy
import sys
sys.path.append('~/takeoff/src/offb/scripts')
import sons
from math import cos, sin
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool

current_state1 = State()
current_state2 = State()
current_state3 = State()
offb_set_mode = SetMode

def state_cb1(state):
    global current_state1
    current_state1 = state

def pose_cb1(msg):
    global pose_mom
    pose_mom = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]

def state_cb2(state2):
    global current_state2
    current_state2 = state2

def state_cb3(state3):
    global current_state3
    current_state3 = state3

state_sub1 = rospy.Subscriber("uav1/mavros/state", State, state_cb1)
local_pos_pub1 = rospy.Publisher("uav1/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_sub1 = rospy.Subscriber("uav1/mavros/local_position/pose", PoseStamped, pose_cb1)
arming_client1 = rospy.ServiceProxy("uav1/mavros/cmd/arming", CommandBool)
set_mode_client1 = rospy.ServiceProxy("uav1/mavros/set_mode", SetMode)

state_sub2 = rospy.Subscriber("uav2/mavros/state", State, state_cb2)
local_pos_pub2 = rospy.Publisher("uav2/mavros/setpoint_position/local", PoseStamped, queue_size=10)
arming_client2 = rospy.ServiceProxy("uav2/mavros/cmd/arming", CommandBool)
set_mode_client2 = rospy.ServiceProxy("uav2/mavros/set_mode", SetMode)

state_sub3 = rospy.Subscriber("uav3/mavros/state", State, state_cb3)
local_pos_pub3 = rospy.Publisher("uav3/mavros/setpoint_position/local", PoseStamped, queue_size=10)
arming_client3 = rospy.ServiceProxy("uav3/mavros/cmd/arming", CommandBool)
set_mode_client3 = rospy.ServiceProxy("uav3/mavros/set_mode", SetMode)

r = 20
z = 1
x = 0
pose1 = PoseStamped()


numberofsons = 2


if __name__ == '__main__':

    try:

	rospy.init_node('offb_node', anonymous = True)
	rate = rospy.Rate(50)

	"""for i in range(100):
	    local_pos_pub1.publish(pose1)
	    rate.sleep()"""

	while not (current_state1.connected and current_state2.connected and current_state3.connected):
	    rate.sleep()

	last_request = rospy.get_rostime()

	while not rospy.is_shutdown():
	    now = rospy.get_rostime()
    	    if current_state1.mode != "OFFBOARD" and current_state2.mode != "OFFBOARD" and current_state3.mode != "OFFBOARD" and (now - last_request > rospy.Duration(5)):
	        set_mode_client1(base_mode=0, custom_mode="OFFBOARD")
	        set_mode_client2(base_mode=0, custom_mode="OFFBOARD")
	        set_mode_client3(base_mode=0, custom_mode="OFFBOARD")
	        last_request = now
	    else:
	        if not current_state1.armed and not current_state2.armed and not current_state3.armed and (now - last_request > rospy.Duration(5)):
		   arming_client1(True)
		   arming_client2(True)
		   arming_client3(True)
		   last_requets = now
	    pose1.pose.position.x = r*cos(x)
	    pose1.pose.position.y = r*sin(x)
	    pose1.pose.position.z = z
	    pose1.header.stamp = rospy.Time.now()
	    local_pos_pub1.publish(pose1)
            sons.updateSonLocation(numberofsons, pose_mom)
            x += 0.01
	    rate.sleep()

    except rospy.ROSInterruptException:
	pass
