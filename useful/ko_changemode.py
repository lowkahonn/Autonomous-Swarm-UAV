#!/usr/bin/env python

import rospy
import sys
import pygame
sys.path.append('~/takeoff/src/offb/src')
import ko_shapes
from math import sin, cos, pi, sqrt
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import SetMode, CommandBool, CommandHome

current_state1 = State()
current_state2 = State()
current_state3 = State()
current_state4 = State()
current_state5 = State()
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

def pose_cb4(msg4):
    global pos4
    pos4 = [msg4.pose.position.x, msg4.pose.position.y, msg4.pose.position.z]

def pose_cb5(msg5):
    global pos5
    pos5 = [msg5.pose.position.x, msg5.pose.position.y, msg5.pose.position.z]

def state_cb1(state):
    global current_state1
    current_state1 = state

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

def setup_all_uavs(set_mode_client, arming_client):
    if current_state1.mode != "OFFBOARD" and current_state2.mode != "OFFBOARD" and current_state3.mode != "OFFBOARD" and current_state4.mode != "OFFBOARD" and current_state5.mode != "OFFBOARD":
        for i in range(len(set_mode_client)):
            set_mode_client[i](base_mode=0, custom_mode="OFFBOARD")
    else:
        if not (current_state1.armed and current_state2.armed and current_state3.armed and current_state4.armed and current_state5.armed):
            for i in range(len(arming_client)):
                arming_client[i](True)

def set_up_subs_and_pubs():
    global pose_pub, pose, set_mode_client, arming_client, location
    # subscribers
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
    # publishers
    local_pos_pub1 = rospy.Publisher("uav1/mavros/setpoint_position/local", PoseStamped, queue_size=10)
    local_pos_pub2 = rospy.Publisher("uav2/mavros/setpoint_position/local", PoseStamped, queue_size=10)
    local_pos_pub3 = rospy.Publisher("uav3/mavros/setpoint_position/local", PoseStamped, queue_size=10)
    local_pos_pub4 = rospy.Publisher("uav4/mavros/setpoint_position/local", PoseStamped, queue_size=10)
    local_pos_pub5 = rospy.Publisher("uav5/mavros/setpoint_position/local", PoseStamped, queue_size=10)
    # services
    arming_client1 = rospy.ServiceProxy("uav1/mavros/cmd/arming", CommandBool)
    arming_client2 = rospy.ServiceProxy("uav2/mavros/cmd/arming", CommandBool)
    arming_client3 = rospy.ServiceProxy("uav3/mavros/cmd/arming", CommandBool)
    arming_client4 = rospy.ServiceProxy("uav4/mavros/cmd/arming", CommandBool)
    arming_client5 = rospy.ServiceProxy("uav5/mavros/cmd/arming", CommandBool)
    set_mode_client1 = rospy.ServiceProxy("uav1/mavros/set_mode", SetMode)
    set_mode_client2 = rospy.ServiceProxy("uav2/mavros/set_mode", SetMode)
    set_mode_client3 = rospy.ServiceProxy("uav3/mavros/set_mode", SetMode)
    set_mode_client4 = rospy.ServiceProxy("uav4/mavros/set_mode", SetMode)
    set_mode_client5 = rospy.ServiceProxy("uav5/mavros/set_mode", SetMode)
    # define pose
    pose1 = PoseStamped()
    pose2 = PoseStamped()
    pose3 = PoseStamped()
    pose4 = PoseStamped()
    pose5 = PoseStamped()
    # define global variables
    pose = [pose1, pose2, pose3, pose4, pose5]
    pose_pub = [local_pos_pub1,local_pos_pub2,local_pos_pub3,local_pos_pub4,local_pos_pub5]
    set_mode_client = [set_mode_client1, set_mode_client2, set_mode_client3, set_mode_client4, set_mode_client5]
    arming_client = [arming_client1, arming_client2, arming_client3, arming_client4, arming_client5]
    location = [pos1, pos2, pos3, pos4, pos5]

# **************************************

# ******** CHECK SWARM STATUS **********

def check_numuav(connection):
    num = 0
    for i in range(len(connection)):
	if connection[i]:
	    num += 1
    return num

def check_dist(uavpose1, uavpose2, offset1,offset2):
    near = False
    a = uavpose1[0]- offset1 -uavpose2[0] +offset2
    b = uavpose1[1]-uavpose2[1]
    distance = sqrt(a**2+b**2)
    if distance < 1.5:
	#print distance
	    near = True
    return near

def check_connection(states, direction, uavpose, offset):
    connection = True
    center = [direction[0], direction[1], 3]
    if states.armed:
    	for i in range(len(uavpose)):
            if i == 0:
                Distance = center[i]-(uavpose[i]-offset)
            else:
                Distance = center[i]-(uavpose[i])
            if abs(Distance) > 5:
                connection = False
    else:
	    connection = False
    return connection

def pick_active_uavs(location, pose, direction, current_num_uav, offset, connection):
    my_location = []
    my_offset = []
    for i, connected in enumerate(connection):
	if connected:
            my_location.append(location[i])
            my_offset.append(offset[i])

    values = {
	'location': my_location,
	'pose': pose,
	'direction': direction,
	'numuav': current_num_uav,
	'offset': my_offset,
	'connection': connection
    }
    return values

# *****************************************************

# ************** SET UP SUBS AND PUBS *****************

set_up_subs_and_pubs()

# ****************************************************

WHITE = (255,255,255)
BLACK = (0,0,0)
r = 2
t = 2
dx = 0
dy = 0
direction = [dx, dy]
z = 3
offset = [0,2,-2,4,-4]
numuav = 0
shape = ''

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
        xform = mytext.render("X Shape - Press 'X'", False, WHITE)
        triangle = mytext.render("Triangle - Press 'T'", False, WHITE)
        line = mytext.render("Line - Press 'L'", False, WHITE)
        control = mytext.render("Use arrow keys to control swarm", False, WHITE)
        
	# ********************************************

        rospy.init_node('offb_node', anonymous = True)
        rate = rospy.Rate(20)

        while not (current_state1.connected and current_state2.connected and current_state3.connected and current_state4.connected and current_state5.connected):
            rate.sleep()

        while not rospy.is_shutdown():

            # ************** PRINT WORDS ON PYGAME WINDOW *******************
                
            surface.blit(select_mode, (50, 50))
            surface.blit(circle, (50, 150))
            surface.blit(xform, (50, 250))
            surface.blit(triangle, (50, 350))
            surface.blit(line, (50, 450))
            surface.blit(control, (50, 550))
            screen.blit(surface, (0,0))
            surface.fill(BLACK)
            clock = pygame.time.Clock()
            clock.tick(20) 
            pygame.display.flip()

            # ****************************************************************
        
            setup_all_uavs(set_mode_client, arming_client)

            move = [0,0]
            connection = []
            location = [pos1, pos2, pos3, pos4, pos5]
            #pose = [pose1, pose2, pose3, pose4, pose5]
            current_state = [current_state1, current_state2, current_state3, current_state4, current_state5]

            for i in range(len(current_state)):
            connection.append(check_connection(current_state[i], direction, location[i], offset[i]))
        
            current_num_uav = check_numuav(connection)
            if numuav != current_num_uav:
                if shape:
                    if shape == 'circle':
                        values = pick_active_uavs(location, pose, direction, current_num_uav, offset, connection)
                        pose = ko_shapes.circle(values['location'], values['pose'], values['direction'], values['numuav'], values['offset'], values['connection'])
                numuav = current_num_uav
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o:
                        pose = ko_shapes.circle(location, pose, direction, numuav, offset, connection)
                        shape = 'circle'

                    if event.key == pygame.K_x:
                        pose = ko_shapes.xform(location, pose, direction, numuav, offset)
                        shape = 'xform'

                    if event.key == pygame.K_t:
                        pose = ko_shapes.triangle(location, pose, direction, numuav, offset)
                        shape = 'triangle'

                    if event.key == pygame.K_l:
                        pose = ko_shapes.line(location, pose, direction, numuav, offset)
                        shape = 'line'
            
            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                direction[1] += 0.05
                move[1] += 0.05
            if keys[pygame.K_DOWN]:
                direction[1] -= 0.05
                move[1] -= 0.05
            if keys[pygame.K_RIGHT]:
                direction[0] += 0.05
                move[0] += 0.05
            if keys[pygame.K_LEFT]:
                direction[0] -= 0.05
                move[0] -= 0.05
            

            for i in range(numuav):
                pose[i].pose.position.x += move[0]
                pose[i].pose.position.y += move[1]

            for i in range(5):
                for j in range(5):
                    if j>i:
                        if check_dist(location[i],location[j],offset[i],offset[j]):
                            pose[i].pose.position.z = 4
                            pose[j].pose.position.z = 2
                        else:
                            pose[i].pose.position.z = 3
                            pose[j].pose.position.z = 3
            

            for i in range(5):
                if location[i][2] <0.5:
                    pose[i].pose.position.x = location[i][0]
                    pose[i].pose.position.y = location[i][1]
                    pose[i].pose.position.z = 3
                        
            for i in range(5):
                pose[i].header.stamp = rospy.Time.now()
                pose_pub[i].publish(pose[i])
        
            rate.sleep()

    except rospy.ROSInterruptException:
	pass
