#!/usr/bin/env python

import rospy
import sys
sys.path.append('~/takeoff/src/offb/src')
import sons
from math import sin, cos, pi
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool, CommandHome
#from sensor_msgs.msg import Imu



current_state1 = State()
current_state2 = State()
current_state3 = State()
current_state4 = State()
current_state5 = State()
offb_set_mode = SetMode



def state_cb1(state):
    global current_state1
    current_state1 = state

def pose_cb1(msg1):
    global pos1
    pos1 = [msg1.pose.position.x, msg1.pose.position.y, msg1.pose.position.z]

def pose_cb2(msg2):
    global pos2
    pos2 = [msg2.pose.position.x, msg2.pose.position.y, msg2.pose.position.z]

def pose_cb3(msg3):
    global pos3
    pos3 = [msg3.pose.position.x, msg3.pose.position.y, msg3.pose.position.z]

def pose_cb4(msg4):
    global pos4
    pos4 = [msg4.pose.position.x, msg4.pose.position.y, msg4.pose.position.z]

def pose_cb5(msg5):
    global pos5
    pos5 = [msg5.pose.position.x, msg5.pose.position.y, msg5.pose.position.z]

def state_cb2(state2):
    global current_state2
    current_state2 = state2

def state_cb3(state3):
    global current_state3
    current_state3 = state3

def state_cb4(state4):
    global current_state4
    current_state4 = state4

def state_cb5(state5):
    global current_state5
    current_state5 = state5

def check_numuav(connection):
    global numuav
    numuav = 0
    for i in range(len(connection)):
	if connection[i]:
	    numuav += 1

    
def check_dist(states, center,uavpose, offset):
    connection = True
    if states.armed:
    	for i in range(len(uavpose)):
		if i == 0:
			Distance = center[i]-(uavpose[i]+offset)
		else:
			Distance = center[i]-(uavpose[i])
    		if abs(Distance) > 5:
			connection = False
			print i,center[i],uavpose[i]+offset, Distance
    else:
	connection = False
    return connection

#imu_sub = rospy.Subscriber("uav1/mavros/imu/data", Imu, imu_cb)

# sub
rospy.Subscriber("uav1/mavros/state", State, state_cb1)
rospy.Subscriber("uav2/mavros/state", State, state_cb2)
rospy.Subscriber("uav3/mavros/state", State, state_cb3)
rospy.Subscriber("uav4/mavros/state", State, state_cb4)
rospy.Subscriber("uav5/mavros/state", State, state_cb5)
rospy.Subscriber("uav1/mavros/local_position/pose", PoseStamped, pose_cb1)
rospy.Subscriber("uav2/mavros/local_position/pose", PoseStamped, pose_cb2)
rospy.Subscriber("uav3/mavros/local_position/pose", PoseStamped, pose_cb3)
rospy.Subscriber("uav4/mavros/local_position/pose", PoseStamped, pose_cb4)
rospy.Subscriber("uav5/mavros/local_position/pose", PoseStamped, pose_cb5)


# pub
local_pos_pub1 = rospy.Publisher("uav1/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_pub2 = rospy.Publisher("uav2/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_pub3 = rospy.Publisher("uav3/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_pub4 = rospy.Publisher("uav4/mavros/setpoint_position/local", PoseStamped, queue_size=10)
local_pos_pub5 = rospy.Publisher("uav5/mavros/setpoint_position/local", PoseStamped, queue_size=10)
# service
arming_client1 = rospy.ServiceProxy("uav1/mavros/cmd/arming", CommandBool)
set_home1 = rospy.ServiceProxy("uav1/mavros/cmd/set_home", CommandHome)
set_mode_client1 = rospy.ServiceProxy("uav1/mavros/set_mode", SetMode)
arming_client2 = rospy.ServiceProxy("uav2/mavros/cmd/arming", CommandBool)
set_home2 = rospy.ServiceProxy("uav2/mavros/cmd/set_home", CommandHome)
set_mode_client2 = rospy.ServiceProxy("uav2/mavros/set_mode", SetMode)
arming_client3 = rospy.ServiceProxy("uav3/mavros/cmd/arming", CommandBool)
set_home3 = rospy.ServiceProxy("uav3/mavros/cmd/set_home", CommandHome)
set_mode_client3 = rospy.ServiceProxy("uav3/mavros/set_mode", SetMode)
arming_client4 = rospy.ServiceProxy("uav4/mavros/cmd/arming", CommandBool)
set_mode_client4 = rospy.ServiceProxy("uav4/mavros/set_mode", SetMode)
arming_client5 = rospy.ServiceProxy("uav5/mavros/cmd/arming", CommandBool)
set_mode_client5 = rospy.ServiceProxy("uav5/mavros/set_mode", SetMode)

pose1 = PoseStamped()
pose2 = PoseStamped()
pose3 = PoseStamped()
pose4 = PoseStamped()
pose5 = PoseStamped()



r = 2
t = 2
c = 0
z = 3
center = [0, 0, 0]



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
    	    if current_state1.mode != "OFFBOARD" and current_state2.mode != "OFFBOARD" and current_state3.mode != "OFFBOARD" and (now - last_request > rospy.Duration(3)):
	        set_mode_client1(base_mode=0, custom_mode="OFFBOARD")
	        set_mode_client2(base_mode=0, custom_mode="OFFBOARD")
	        set_mode_client3(base_mode=0, custom_mode="OFFBOARD")
		set_mode_client4(base_mode=0, custom_mode="OFFBOARD")
		set_mode_client5(base_mode=0, custom_mode="OFFBOARD")
	        last_request = now
	    else:
	        if not current_state1.armed and not current_state2.armed and not current_state3.armed and (now - last_request > rospy.Duration(3)):
		   arming_client1(True)
		   arming_client2(True)
		   arming_client3(True)
		   arming_client4(True)
		   arming_client5(True)
		   last_request = now

            #print "center", center, " mom", pose_mom, " son1", pose_son1, " son2", pose_son2," uav4", pose_uav4," uav5", pose_uav5
	    connection = []
	    pose = [pos1, pos2, pos3, pos4, pos5]
	    offset = [0, -2, 2, -4, 4]
	    current_state = [current_state1, current_state2, current_state3, current_state4, current_state5]
	    for i in range(len(current_state)):
		connection.append(check_dist(current_state[i], center, pose[i], offset[i]))
            check_numuav(connection)
	    #print Disconnect	

	    angle = []
            q = 0
	    form = 0
	
	    if numuav > 0:
	    	div = 2*pi/numuav

		for i in range(numuav):
			a = (numuav - i)*div
			angle.append(a)
			form = 1
			
	    #print numuav, angle
	
	    if pos5[2] > 1 and form == 1 and connection[4]:
		x5 = r*cos(angle[q]) - 4 + t*cos(c)
		y5 = r*sin(angle[q]) + t*sin(c) 
	    	pose5.pose.position.x = x5 
            	pose5.pose.position.y = y5 
		pose5.pose.position.z = z
		q += 1
		

	    elif c==0:
		x5 = pos5[0]
		y5 = pos5[1]
		pose5.pose.position.x = x5
            	pose5.pose.position.y = y5
		pose5.pose.position.z = z
	    
	    if pos3[2] > 1 and form == 1 and connection[2]:
		x3 = r*cos(angle[q]) - 2 + t*cos(c)
		y3 = r*sin(angle[q]) + t*sin(c) 
	    	pose3.pose.position.x = x3 
            	pose3.pose.position.y = y3 
		pose3.pose.position.z = z
		q += 1
		

	    elif c==0:
		x3 = pos3[0]
		y3 = pos3[1]
		pose3.pose.position.x = x3
            	pose3.pose.position.y = y3
		pose3.pose.position.z = z

	    if pos2[2] > 1 and form == 1 and connection[1]:
		x2 = r*cos(angle[q]) + 2 + t*cos(c)
		y2 = r*sin(angle[q]) + t*sin(c)
	    	pose2.pose.position.x = x2 
            	pose2.pose.position.y = y2 
		pose2.pose.position.z = z 
		q += 1
		

	    elif c==0:
		x2 = pos2[0]
		y2 = pos2[1]
		pose2.pose.position.x = x2 
            	pose2.pose.position.y = y2 
		pose2.pose.position.z = z 

	    if pos4[2] > 1 and form == 1 and connection[3]:
		x4 = r*cos(angle[q]) + 4 + t*cos(c)
		y4 = r*sin(angle[q]) + t*sin(c) 
	    	pose4.pose.position.x = x4 
            	pose4.pose.position.y = y4 
		pose4.pose.position.z = z
		q += 1
		

	    elif c==0:
		x4 = pos4[0]
		y4 = pos4[1]
		pose4.pose.position.x = x4
            	pose4.pose.position.y = y4
		pose4.pose.position.z = z

            if pos1[2] > 1 and form == 1 and connection[0]: 
		x1 = r*cos(angle[q]) + t*cos(c)
		y1 = r*sin(angle[q]) + t*sin(c)
            	pose1.pose.position.x = x1 
            	pose1.pose.position.y = y1  
		pose1.pose.position.z = z
		q += 1
		

	    elif c==0:
		x1 = pos1[0]
		y1 = pos1[1]
		pose1.pose.position.x = x1 
            	pose1.pose.position.y = y1 
	 	pose1.pose.position.z = z 
	    
		
	    pose1.header.stamp = rospy.Time.now()
	    pose2.header.stamp = rospy.Time.now()
            pose3.header.stamp = rospy.Time.now()
	    pose4.header.stamp = rospy.Time.now()
	    pose5.header.stamp = rospy.Time.now()

	    local_pos_pub1.publish(pose1)
	    local_pos_pub2.publish(pose2)
	    local_pos_pub3.publish(pose3)
	    local_pos_pub4.publish(pose4)
	    local_pos_pub5.publish(pose5)
	    print pose1
            """sons.updateSonLocation(numberofsons, pose_mom, vel_mom)""" 
	    
	    if pos1[2] > 2.5 or pos2[2] > 2.5 or pos3[2] > 2.5 or pos4[2] > 2.5 or pos5[2] > 2.5:
	    	c += 0.05
		center = [t*cos(c), t*sin(c), z]
		
	    
	    
            
	    rate.sleep()

    except rospy.ROSInterruptException:
	pass
