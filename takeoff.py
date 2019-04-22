#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool

current_state1 = State()
"""current_state2 = State
current_state3 = State"""
offb_set_mode = SetMode
numuav = 2
testvar = []


# ***************************************************************************
# this function is to test if callback function can be called and can store the posestamped into a global list.

def getTopicList(uav):
    topic = []
    for i in range(uav):
	top = "uav" + str(i+1) + '/mavros/local_position/pose'
        topic.append(top)
    return topic

def testcb(msg, args):
    global testvar
    cb_args = args
    location = [msg.pose.position.x, msg.pose.position.y, msg.pose.position.z]
    testvar.insert(cb_args % numuav, location)
    if len(testvar) > numuav:
	del testvar[-1]
    print "location", testvar

    """# modulus of anything of 0 is 0, so place the first term in index 0
	if i == 0:
	   testvar.append(msg)
	else:
	   testvar.insert(i % numuav, msg)"""


    # define a global list to store the posestamped variables
    # if the length of this list is equal to the number of uavs
	# wait for message, then put it into the list (uav1 into index 0, uav2 into index 1, ...)


    # replace topic with topic lists of multiple uav


# IDEA TWO!!!
"""
USE NORMAL SUBSCRIBER BUT MODIFY THE CALLBACK FUNCTION

1. NEED AN IDENTIFIER TO KNOW WHERE THE MESSAGE COME FROM. 
   E.G. IF THE MESSAGE COMES FROM UAV1, PUT THE MESSAGE INTO INDEX 0, OR IF IT IS FROM UAV4, PUT IT INTO INDEX 3


"""

# *****************************************************************************

def state_cb1(state):
    global current_state1
    current_state1 = state



state_sub1 = rospy.Subscriber("uav1/mavros/state", State, state_cb1)
local_pos_pub1 = rospy.Publisher("uav1/mavros/setpoint_position/local", PoseStamped, queue_size=10)
arming_client1 = rospy.ServiceProxy("uav1/mavros/cmd/arming", CommandBool)
set_mode_client1 = rospy.ServiceProxy("uav1/mavros/set_mode", SetMode)

pose1 = PoseStamped()
pose1.pose.position.x = 0
pose1.pose.position.y = 0
pose1.pose.position.z = 3

subTopics = getTopicList(numuav)

for i in range(numuav):
    rospy.Subscriber(subTopics[i], PoseStamped, testcb, callback_args = i)
    

if __name__ == '__main__':

    try:

	rospy.init_node('offb_node', anonymous = True)
	rate = rospy.Rate(20)

	for i in range(100):
	    local_pos_pub1.publish(pose1)
	    rate.sleep()

	while not current_state1.connected:
	    rate.sleep()

	last_request = rospy.get_rostime()

	while not rospy.is_shutdown():
	    now = rospy.get_rostime()
    	    if current_state1.mode != "OFFBOARD" and (now - last_request > rospy.Duration(5)):
	        set_mode_client1(base_mode=0, custom_mode="OFFBOARD")
	        last_request = now
	    else:
	        if not current_state1.armed and (now - last_request > rospy.Duration(5)):
		   arming_client1(True)
		   last_requets = now

	    pose1.header.stamp = rospy.Time.now()
	    local_pos_pub1.publish(pose1)
	    rate.sleep()

    except rospy.ROSInterruptException:
	pass
