#!/usr/bin/env python

import rospy
import sys
sys.path.append('~/takeoff/src/offb/src')
import sons
from math import sin,cos, pi
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool
#from sensor_msgs.msg import Imu

current_state1 = State()
current_state2 = State()
current_state3 = State()
offb_set_mode = SetMode

def state_cb1(state):
    global current_state1
    current_state1 = state

def pose_cb1(msg1):
    global pose_mom
    pose_mom = [msg1.pose.position.x, msg1.pose.position.y, msg1.pose.position.z]

def pose_cb2(msg2):
    global pose_son1
    pose_son1 = [msg2.pose.position.x, msg2.pose.position.y, msg2.pose.position.z]

def pose_cb3(msg3):
    global pose_son2
    pose_son2 = [msg3.pose.position.x, msg3.pose.position.y, msg3.pose.position.z]

def state_cb2(state2):
    global current_state2
    current_state2 = state2

def state_cb3(state3):
    global current_state3
    current_state3 = state3

"""def imu_cb(data):
    global imu_1
    imu_1 = data
    print imu_1"""

#imu_sub = rospy.Subscriber("uav1/mavros/imu/data", Imu, imu_cb)

# sub
rospy.Subscriber("uav1/mavros/state", State, state_cb1)
rospy.Subscriber("uav2/mavros/state", State, state_cb2)
rospy.Subscriber("uav3/mavros/state", State, state_cb3)
rospy.Subscriber("uav1/mavros/local_position/pose", PoseStamped, pose_cb1)
rospy.Subscriber("uav2/mavros/local_position/pose", PoseStamped, pose_cb2)
rospy.Subscriber("uav3/mavros/local_position/pose", PoseStamped, pose_cb3)

# pub
local_pos_pub1 = rospy.Publisher("uav1/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_pub2 = rospy.Publisher("uav2/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_pub3 = rospy.Publisher("uav3/mavros/setpoint_position/local", PoseStamped, queue_size=10)
# service
arming_client1 = rospy.ServiceProxy("uav1/mavros/cmd/arming", CommandBool)
set_mode_client1 = rospy.ServiceProxy("uav1/mavros/set_mode", SetMode)
arming_client2 = rospy.ServiceProxy("uav2/mavros/cmd/arming", CommandBool)
set_mode_client2 = rospy.ServiceProxy("uav2/mavros/set_mode", SetMode)
arming_client3 = rospy.ServiceProxy("uav3/mavros/cmd/arming", CommandBool)
set_mode_client3 = rospy.ServiceProxy("uav3/mavros/set_mode", SetMode)

pose1 = PoseStamped()
pose2 = PoseStamped()
pose3 = PoseStamped()


r = 1
t = 5
c = 0
z = 3


numberofsons = 2

if __name__ == '__main__':

    try:

	rospy.init_node('offb_node', anonymous = True)
	rate = rospy.Rate(20)

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
		   last_request = now


            if pose_mom[2] > 0.5: 
		x1 = r*cos(4*pi/3)
		y1 = r*sin(4*pi/3) 
            	pose1.pose.position.x = x1 + t*cos(c)
            	pose1.pose.position.y = y1 + t*sin(c)
		pose1.pose.position.z = z

	    else:
		x1 = pose_mom[0]
		y1 = pose_mom[1]
		pose1.pose.position.x = x1 
            	pose1.pose.position.y = y1 
	 	pose1.pose.position.z = z 

	    if pose_son1[2] > 0.5:
		x2 = r*cos(2*pi/3) + 2
		y2 = r*sin(2*pi/3)
	    	pose2.pose.position.x = x2 + t*cos(c)
            	pose2.pose.position.y = y2 + t*sin(c)
		pose2.pose.position.z = z 

	    else:
		x2 = pose_son1[0]
		y2 = pose_son1[1]
		pose2.pose.position.x = x2 
            	pose2.pose.position.y = y2 
		pose2.pose.position.z = z 

	    if pose_son2[2] > 0.5:
		x3 = r*cos(2*pi) - 2
		y3 = r*sin(2*pi)
	    	pose3.pose.position.x = x3 + t*cos(c)
            	pose3.pose.position.y = y3 + t*sin(c)
		pose3.pose.position.z = z

	    else:
		x3 = pose_son2[0]
		y3 = pose_son2[1]
		pose3.pose.position.x = x3
            	pose3.pose.position.y = y3
		pose3.pose.position.z = z

	    pose1.header.stamp = rospy.Time.now()
	    pose2.header.stamp = rospy.Time.now()
            pose3.header.stamp = rospy.Time.now()

	    local_pos_pub1.publish(pose1)
	    local_pos_pub2.publish(pose2)
	    local_pos_pub3.publish(pose3)
            """sons.updateSonLocation(numberofsons, pose_mom, vel_mom)""" 

	    if pose_mom[2] > 2.5 and pose_son1[2] > 2.5 and pose_son2[2] > 2.5:
	    	c += 0.1
	    


	    rate.sleep()

    except rospy.ROSInterruptException:
	pass
