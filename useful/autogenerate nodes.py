#!/usr/bin/env python

""" 
********** TO DO LIST **************
1. FIND A WAY TO LISTEN TO KEYBOARD!!
2. CHANGE SHAPE, DISARM!
************************************
"""

import pygame
import rospy
from math import sin, cos, pi
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool

def getPoseTopicList(uav):
    topic = []
    for i in range(uav):
	top = "uav" + str(i+1) + '/mavros/local_position/pose'
        topic.append(top)
    return topic

def getPosePublishList(uav):
    topic = []
    for i in range(uav):
	top = "uav" + str(i+1) + '/mavros/setpoint_position/local'
        topic.append(top)
    return topic

def getStateTopicList(uav):
    topic = []
    for i in range(uav):
	top = "uav" + str(i+1) + '/mavros/state'
        topic.append(top)
    return topic

def posecb(msg, args):
    global location
    cb_args = args
    loc = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]
    location.insert(cb_args % numuav, loc)
    if len(location) > numuav:
	del location[cb_args + 1]

def statecb(msg, args):
    global current_state
    cb_args = args
    current_state[cb_args] = msg

def check_numuav(connection):
    global uav_in_swarm
    uav_in_swarm = 0
    for i in range(len(connection)):
	if connection[i]:
	    uav_in_swarm += 1

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
			#print i,center[i],uavpose[i]+offset, Distance
    else:
	connection = False
    return connection

def test_func(pose):
    pose.pose.position.x=0
    pose.pose.position.y=0
    pose.pose.position.z=3
    return pose

if __name__ == '__main__':

    try:

	pygame.init()
	screen = pygame.display.set_mode((400,400))
	rospy.init_node('offb_node', anonymous = True)
	rate = rospy.Rate(20)
	location = []
	numuav = int(input('How many UAVs are there in the system? '))
	uav_in_swarm = 0
	current_state = [State() for i in range(numuav)]
	# sub
	posetopic = getPoseTopicList(numuav)
	statetopic = getStateTopicList(numuav)
	for i in range(numuav):
	    rospy.Subscriber(statetopic[i], State, statecb, callback_args = i)
	    rospy.Subscriber(posetopic[i], PoseStamped, posecb, callback_args = i)

	# pub
	publishtopic = getPosePublishList(numuav)
	publish_list = []
	for i in range(numuav):
	    publish_list.append(rospy.Publisher(publishtopic[i], PoseStamped, queue_size=10))

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
	t = 3
	c = 0	
	z = 3

	center = [0, 0, 0]	

	while not (current_state[0].connected and current_state[1].connected and current_state[2].connected):
	    rate.sleep()

	last_request = rospy.get_rostime()

	while not rospy.is_shutdown():
	    now = rospy.get_rostime()

	    # initialization
    	    if current_state[0].mode != "OFFBOARD" and current_state[2].mode != "OFFBOARD" and current_state[2].mode != "OFFBOARD" and (now - last_request > rospy.Duration(3)):
	        set_mode_client1(base_mode=0, custom_mode="OFFBOARD")
	        set_mode_client2(base_mode=0, custom_mode="OFFBOARD")
	        set_mode_client3(base_mode=0, custom_mode="OFFBOARD")
	        last_request = now
	    else:
	        if not current_state[0].armed and not current_state[1].armed and not current_state[2].armed and (now - last_request > rospy.Duration(3)):
		   arming_client1(True)
		   arming_client2(True)
		   arming_client3(True)
		   last_request = now
	    

	    for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
		   if event.key == pygame.K_t:
		   	pose2 = test_func(pose2)
			pose2.header.stamp = rospy.Time.now()
			publish_list[1].publish(pose2)

	    # angle assignments
            connection = []
	    offset = [0, -2, 2]
	    if len(location) != 0:
		for i in range(len(current_state)):
		   connection.append(check_dist(current_state[i], center, location[i], offset[i]))
		check_numuav(connection)

	    angle = []
            q = 0
	    form = 0
	
	    if uav_in_swarm > 0:
	    	div = 2*pi/uav_in_swarm

		for i in range(uav_in_swarm):
			a = (uav_in_swarm - i)*div
			angle.append(a)
			form = 1
	
	    # setpoint locations
	    # uav3
	    if location[2][2] > 1 and form == 1 and connection[2]:
		x3 = r*cos(angle[q]) - 2 + c
		y3 = r*sin(angle[q]) + 0.5 * c **2
	    	pose3.pose.position.x = x3 
            	pose3.pose.position.y = y3 
		pose3.pose.position.z = z
		del angle[0]

		
	    elif c==0:
		x3 = location[2][0]
		y3 = location[2][1]
		pose3.pose.position.x = x3
            	pose3.pose.position.y = y3
		pose3.pose.position.z = z


	    # uav2
	    if location[1][2] > 1 and form == 1 and connection[1]:
		x2 = r*cos(angle[q]) + 2 + c
		y2 = r*sin(angle[q]) + 0.5 * c ** 2
	    	pose2.pose.position.x = x2 
            	pose2.pose.position.y = y2 
		pose2.pose.position.z = z 
		del angle[0]
		
	    elif c==0:
		x2 = location[1][0]
		y2 = location[1][1]
		pose2.pose.position.x = x2 
            	pose2.pose.position.y = y2 
		pose2.pose.position.z = z 


	    # uav1
            if location[0][2] > 1 and form == 1 and connection[0]: 
		x1 = r*cos(angle[q]) + c
		y1 = r*sin(angle[q]) + 0.5 * c ** 2
            	pose1.pose.position.x = x1 
            	pose1.pose.position.y = y1  
		pose1.pose.position.z = z
		del angle[0]

	    elif c==0:
		x1 = location[0][0]
		y1 = location[0][1]
		pose1.pose.position.x = x1 
            	pose1.pose.position.y = y1 
	 	pose1.pose.position.z = z 
	    
	    pose1.header.stamp = rospy.Time.now()
	    pose2.header.stamp = rospy.Time.now()
            pose3.header.stamp = rospy.Time.now()

	    publish_list[0].publish(pose1)
	    publish_list[1].publish(pose2)
	    publish_list[2].publish(pose3)

	    #print 'connection', connection

	    if uav_in_swarm > 0 and len(angle) == 0:
	    	c += 0.05
		center = [c, 0.5 * c ** 2, z]

	    rate.sleep()

    except rospy.ROSInterruptException:
	pass
