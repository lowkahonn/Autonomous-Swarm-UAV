#!/usr/bin/env python

import rospy
import sys
import pygame
sys.path.append('~/takeoff/src/offb/src')
import vicon_shapes
from math import sin, cos, pi, sqrt
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool, CommandHome

current_state1 = State()
current_state2 = State()
current_state3 = State()

offb_set_mode = SetMode

# ****** SET UP SUBSCRIBERS CALL BACK ********

def pose_cb1(msg1):
    global pos1
    pos1 = [msg1.pose.position.x, msg1.pose.position.y, msg1.pose.position.z]

def pose_cb2(msg2):
    global pos2
    pos2 = [msg2.pose.position.x, msg2.pose.position.y, msg2.pose.position.z]

def pose_cb3(msg3):
    global pos3
    pos3 = [msg3.pose.position.x, msg3.pose.position.y, msg3.pose.position.z]

def state_cb1(state):
    global current_state1
    current_state1 = state

def state_cb2(state2):
    global current_state2
    current_state2 = state2

def state_cb3(state3):
    global current_state3
    current_state3 = state3

def setup_all_uavs(set_mode_client, arming_client):
    if current_state1.mode != "OFFBOARD" and current_state2.mode != "OFFBOARD" and current_state3.mode != "OFFBOARD":
	for i in range(len(set_mode_client)):
            set_mode_client[i](base_mode=0, custom_mode="OFFBOARD")
	"""set_mode_client1(base_mode=0, custom_mode="OFFBOARD")
		set_mode_client2(base_mode=0, custom_mode="OFFBOARD")
		set_mode_client3(base_mode=0, custom_mode="OFFBOARD")
		set_mode_client4(base_mode=0, custom_mode="OFFBOARD")
		set_mode_client5(base_mode=0, custom_mode="OFFBOARD")"""
        
    else:
	if not current_state1.armed and not current_state2.armed and not current_state3.armed:
	    for i in range(len(arming_client)):
	        arming_client[i](True)
	    """arming_client1(True)
	    arming_client2(True)
	    arming_client3(True)
	    arming_client4(True)
	    arming_client5(True)"""


def set_up_subs_and_pubs():
    global pose_pub, pose, set_mode_client, arming_client
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

    pose = [pose1, pose2, pose3]
    pose_pub = [local_pos_pub1,local_pos_pub2,local_pos_pub3]
    set_mode_client = [set_mode_client1, set_mode_client2, set_mode_client3]
    arming_client = [arming_client1, arming_client2, arming_client3]

# **************************************

# ******** CHECK SWARM STATUS **********

def check_numuav(connection):
    num = 0
    for i in range(len(connection)):
	if connection[i]:
	    num += 1
    return num

def check_dist(uavpose1, uavpose2):
    near = False
    a = uavpose1[0] - uavpose2[0] 
    b = uavpose1[1]-uavpose2[1]
    distance = sqrt(a**2+b**2)
    if distance < 0.5:
	#print distance
	near = True
    return near

def check_connection(states, uavpose, center):
    connection = True
    if states.armed:
    	for i in range(len(uavpose)):
	    if i == 0:
		Distance = center[i]-(uavpose[i])
	    else:
            	Distance = center[i]-(uavpose[i])
            if abs(Distance) > 2.5:
                connection = False
    else:
	connection = False
    return connection

def pick_active_uavs(location, pose, current_num_uav, connection):
    my_location = []
    my_pose = []
    for i, connected in enumerate(connection):
	if connected:
            my_location.append(location[i])
            my_pose.append(pose[i])

    for p in pose:
	if p not in my_pose:
            my_pose.append(p)

    values = {
	'location': my_location,
	'pose': my_pose,
	'numuav': current_num_uav,
    }
    return values

# *****************************************************

# ************** SET UP SUBS AND PUBS *****************

set_up_subs_and_pubs()

# ****************************************************

WHITE = (255,255,255)
BLACK = (0,0,0)
r = 1
t = 0
z = 1
t = 0
c = 0
cx = 0
cy = 0
numuav = 0
savepose = []
shape = ''
done = False
turning = False
marching = False

# ****************************************************

if __name__ == '__main__':

    try:
	# ************* SET UP PYGAME ****************

        pygame.init()
	pygame.font.init()
	screen = pygame.display.set_mode((600,600))
	surface = pygame.Surface(screen.get_size())
	mytext = pygame.font.SysFont('Comic Sans MS', 35)
        select_mode = mytext.render("Select mode: ", False, WHITE)
        circle = mytext.render("Circle - Press 'O'", False, WHITE)
        line = mytext.render("Line - Press 'L'", False, WHITE)
        turn = mytext.render("Start turning - Press 'T'", False, WHITE)
	march= mytext.render("March - Press 'M'", False, WHITE)
	hold = mytext.render("Hold position - Press 'H'", False, WHITE)

        

	# ********************************************

	rospy.init_node('offb_node', anonymous = True)
	rate = rospy.Rate(20)

	while not (current_state1.connected and current_state2.connected and current_state3.connected):
	    rate.sleep()

	while not done:
	    try:   
		if pos1 and pos2 and pos3:
			done = True
	    except:
		pass

	#last_request = rospy.get_rostime()

	while not rospy.is_shutdown():

	    # ************** PRINT WORDS ON PYGAME WINDOW *******************
            
            surface.blit(select_mode, (50, 50))
            surface.blit(circle, (50, 150))
            surface.blit(line, (50, 250))
            surface.blit(turn, (50, 350))
	    surface.blit(march, (50, 450))
            surface.blit(hold, (50, 550))
            screen.blit(surface, (0,0))
            surface.fill(BLACK)
	    clock = pygame.time.Clock()
	    clock.tick(20) 
	    pygame.display.flip()

	    # ****************************************************************
	   
 	    setup_all_uavs(set_mode_client, arming_client)
	    rate.sleep()
	    connection = []
	    location = [pos1, pos2, pos3]
	    current_state = [current_state1, current_state2, current_state3]
	    center = [cx,cy,z]

	    for i in range(len(current_state)):
		connection.append(check_connection(current_state[i], location[i],center))
	
   	    current_num_uav = check_numuav(connection)
            if numuav != current_num_uav:
		if shape:
                    if shape == 'circle':
                        values = pick_active_uavs(location, pose, current_num_uav, connection)
                        pose = vicon_shapes.circle(values['location'], values['pose'], values['numuav'], t, cy)
		numuav = current_num_uav
	
	    for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o:
                        pose = vicon_shapes.circle(location, pose, numuav, t, cy)
                        shape = 'circle'

		    if event.key == pygame.K_l:
                        pose = vicon_shapes.line(location, pose, numuav)
                        shape = 'line'

                    if event.key == pygame.K_t:
			turning = True

		    if event.key == pygame.K_m:
			marching = True
                       
                    if event.key == pygame.K_h:
			turning = False
			marching = False

            if turning:
		t += 0.015
		pose = vicon_shapes.circle(location, pose, numuav, t, cy)
	
	    if marching:
		c += 0.015
		cy = sin(c)
		if shape == 'line':
			for i in range(numuav):
		    		pose[i].pose.position.y = cy
		
		if shape == 'circle':
			pose = vicon_shapes.circle(location, pose, numuav, t, cy)

 
	    for i in range(numuav):
		for j in range(numuav):
                    if j>i:
                        if check_dist(location[i],location[j]):
                            pose[i].pose.position.z = z + 0.5
                            pose[j].pose.position.z = z - 0.5
                        else:
                            pose[i].pose.position.z = z
                            pose[j].pose.position.z = z
        

	    for i in range(numuav):
		if location[i][2] <0.5:
                    pose[i].pose.position.x = location[i][0]
                    pose[i].pose.position.y = location[i][1]
                    pose[i].pose.position.z = z
                    
	    for i in range(len(pose)):
		pose[i].header.stamp = rospy.Time.now()
		pose_pub[i].publish(pose[i])
	
	    rate.sleep()

    except rospy.ROSInterruptException:
	pass
