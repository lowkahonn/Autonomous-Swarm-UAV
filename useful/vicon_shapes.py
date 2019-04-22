#!/usr/bin/env python

import rospy
from math import cos, sin, pi, sqrt
from itertools import permutations

r=1
z=1


def get_distance(point1,point2):

    return sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def nearest(locations, waypoint):

    # location = [[x1, y1, z1], [x2, y2, z2]]
    # combinations = [([x,y,z],[x1,y1,z1]),([x,y,z],[x1,y1,z1])]
    loc = locations
    wp = waypoint 
    combinations = list(permutations(wp))
    total_travelled = []
    
    for i in range(len(combinations)):
        travelled = 0
        for j in range(len(loc)):
            travelled += get_distance(loc[j], combinations[i][j])
        total_travelled.append(travelled)

    index_minimum = total_travelled.index(min(total_travelled))
    return combinations[index_minimum]	

def circle(location, pose, numuav,turn, sin_c):
    
    waypoints = []
    angle = 2*pi/numuav
    
    for i in range(numuav):
        x = r * cos(angle*(numuav-i)+turn) 
        y = r * sin(angle*(numuav-i)+turn) + sin_c
        waypoints.append([x,y])

    # a points tuple ([x1,y1,z1],[x2,y2,z2])
    points = nearest(location, waypoints)

    for i in range(numuav):
        pose[i].pose.position.x = points[i][0] 
        pose[i].pose.position.y = points[i][1] 
        pose[i].pose.position.z = z
                    
    return pose


def line(location, pose, numuav):
    
    waypoints = [[0,0], [-1,0],[1,0]]

    '''for i in range(len(waypoints)):
        waypoints[i][0] += direction[0]
        waypoints[i][1] += direction[1]'''

    points = nearest(location, waypoints)

    for i in range(numuav):
        if location[i][2] > 0.5:
            pose[i].pose.position.x = points[i][0]  
            pose[i].pose.position.y = points[i][1] 
            pose[i].pose.position.z = z
    return pose


