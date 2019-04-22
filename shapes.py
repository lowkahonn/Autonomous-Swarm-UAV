#!/usr/bin/env python

import rospy
from math import cos, sin, pi, sqrt
from itertools import permutations

r=2
z=3 
offset = [0,2,-2,4,-4]

def get_distance(point1,point2):

    return sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def nearest(locations, waypoint, myoffset):

    # location = [[x1, y1, z1], [x2, y2, z2]]
    # combinations = [([x,y,z],[x1,y1,z1]),([x,y,z],[x1,y1,z1])]
    loc = locations
    wp = waypoint 
    combinations = list(permutations(wp))
    total_travelled = []
    
    # include the offset
    for i in range(len(loc)):
        loc[i][0] -= myoffset[i]

    for i in range(len(combinations)):
        travelled = 0
        for j in range(len(loc)):
            travelled += get_distance(loc[j], combinations[i][j])
        total_travelled.append(travelled)

    index_minimum = total_travelled.index(min(total_travelled))
    return combinations[index_minimum]	

def circle(location, pose, direction, numuav, myoffset):
    
    waypoints = []
    angle = 2*pi/numuav
    
    for i in range(numuav):
        x = r * cos(angle*(numuav-i)) + direction[0]
        y = r * sin(angle*(numuav-i)) + direction[1]
        waypoints.append([x,y])

    # a points tuple ([x1,y1,z1],[x2,y2,z2])
    points = nearest(location, waypoints, myoffset)

    for i in range(numuav):
        pose[i].pose.position.x = points[i][0] + myoffset[i]
        pose[i].pose.position.y = points[i][1]
        pose[i].pose.position.z = z
                    
    return pose


def xform(location, pose, direction, numuav, myoffset):
	
    if numuav < 5:
        return
    else:
        waypoints = [[direction[0], direction[1]]]
        angle = 2*pi/4

        for i in range(4):
            x = r * cos(angle*i+pi/4) + direction[0]
            y = r * sin(angle*i+pi/4) + direction[1]
            waypoints.append([x,y])
        
        points = nearest(location, waypoints, myoffset)

        for i in range(numuav):
            pose[i].pose.position.x = points[i][0] + myoffset[i] 
            pose[i].pose.position.y = points[i][1] 
            pose[i].pose.position.z = z

        return pose

def triangle(location, pose, direction, numuav, myoffset):

    if numuav < 5:
        return
    else:
        waypoints = []
        angle = 2*pi/3
        
        for i in range(3):
            x = r*cos(angle*i + pi/2) + direction[0]
            y = r*sin(angle*i + pi/2) + direction[1]
            waypoints.append([x,y])

        for i in range(2):
            x = waypoints[0][0]+waypoints[i+1][0]
            x /= 2
            y = waypoints[0][1]+waypoints[i+1][1]
            y /= 2
            waypoints.append([x,y])

        points = nearest(location, waypoints, myoffset)
                
        for i in range(5):
            pose[i].pose.position.x = points[i][0] + myoffset[i] 
            pose[i].pose.position.y = points[i][1] 
            pose[i].pose.position.z = z	

        return pose

def line(location, pose, direction, numuav, myoffset):
    
    waypoints = [[0,0], [-2,0],[2,0],[-4,0],[4,0]]

    for i in range(len(waypoints)):
        waypoints[i][0] += direction[0]
        waypoints[i][1] += direction[1]

    points = nearest(location, waypoints, myoffset)

    for i in range(5):
        if location[i][2] > 1:
            pose[i].pose.position.x = points[i][0] + myoffset[i] 
            pose[i].pose.position.y = points[i][1] 
            pose[i].pose.position.z = z
    return pose


