#!/usr/bin/env python

import rospy
from math import cos, sin, pi, sqrt
from itertools import permutations

r=2
z=3 
offset = [0,2,-2,4,-4]

def get_distance(point1,point2):
    return sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)

def nearest(locations, waypoint):
    loc = locations
    wp = waypoint 
    """for i in range(len(loc)):
        loc[i][0] -= offset[i]"""
    combinations = list(permutations(wp))

    total_travelled = []

    for i in range(len(combinations)):
        travelled = 0
        for j in range(len(loc)):
            	travelled += get_distance(loc[j], combinations[i][j])
        total_travelled.append(travelled)

    index_minimum = total_travelled.index(min(total_travelled))

    return combinations[index_minimum]

"""def nearest_point(location, angle, mode, direction):

	op_angle = [None for i in range(len(angle))]
	asg=[]
	if mode == 2:
		xarray=[]
		yarray=[]
		m = 0
	else:
		m = mode
	
	for i in range(len(angle)):
		x = r*cos(angle[i]) + direction[0]
		y = r*sin(angle[i]) + direction[1]
		dist=[]

		if mode == 2:
			if i<3:
				xarray.append(x)
				yarray.append(y)
			if i>2:
				x = (xarray[0]+xarray[i-2])/2
				y = (yarray[0]+yarray[i-2])/2

		for j in range(len(angle)):
			a = location[j+m][0] - offset[j+m] - x
			b = location[j+m][1] - y
			total = a**2+b**2
			dist.append(total)
		minindex = dist.index(min(dist))
		flag = True
		while flag:
			if minindex not in asg:	
				if mode == 2 and i>2:
					op_angle[minindex]=[x,y]
					asg.append(minindex)
					flag = False

				else:
					op_angle[minindex]=angle[i]
					asg.append(minindex)
					flag = False
			else:
				dist[minindex]=99999
				minindex = dist.index(min(dist))
	return op_angle

def settle(ang, optimum, min_index, distance):
	if ang not in optimum and optimum[min_index]== None:
		optimum[min_index] = ang
		return optimum
	else:
		print distance
		if optimum[min_index] != None:
			min_index
		distance[min_index] = 999999
		min_index = distance.index(min(distance))
		settle(ang, optimum, min_index, distance)"""
	

def circle(location, pose, direction, numuav, myoffset,connection):
	waypoints = []
	angle = 2*pi/numuav
	trueloc= location
	loc = []
	
	for i in range(numuav):
 	        x = r * cos(angle*(numuav-i)) + direction[0]
   		y = r * sin(angle*(numuav-i)) + direction[1]
    		waypoints.append([x,y])

	for i in range(len(trueloc)):
        	trueloc[i][0] -= offset[i]

	for i in range(5):
		if connection[i]:
			loc.append(trueloc[i])
	
	print numuav
	points = nearest(loc, waypoints)

	q = 0
	for i in range(5):
		if connection[i]:
			pose[i].pose.position.x = points[q][0] + myoffset[i]
			pose[i].pose.position.y = points[q][1]
			pose[i].pose.position.z = z
			q +=1
	
	return pose


def xform(location, pose, direction):
	waypoints = [[direction[0], direction[1]]]
	angle = 2*pi/4
	trueloc= location

	for i in range(4):
 	        x = r * cos(angle*i+pi/4) + direction[0]
   		y = r * sin(angle*i+pi/4) + direction[1]
    		waypoints.append([x,y])

	for i in range(len(trueloc)):
        	trueloc[i][0] -= offset[i]
	
	points = nearest(trueloc, waypoints)

	for i in range(5):
		pose[i].pose.position.x = points[i][0] + offset[i] 
	    	pose[i].pose.position.y = points[i][1] 
		pose[i].pose.position.z = z

	return pose

def triangle(location, pose, direction):
	waypoints = []
	angle = 2*pi/3
	trueloc = location
	
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

	for i in range(len(trueloc)):
        	trueloc[i][0] -= offset[i]

	points = nearest(trueloc, waypoints)
		
	for i in range(5):
		pose[i].pose.position.x = points[i][0] + offset[i] 
	    	pose[i].pose.position.y = points[i][1] 
		pose[i].pose.position.z = z	

	return pose

def line(location, pose, direction):
	trueloc = location
	waypoints = [[0,0], [-2,0],[2,0],[-4,0],[4,0]]
	for i in range(len(waypoints)):
		waypoints[i][0] += direction[0]
		waypoints[i][1] += direction[1]

	for i in range(len(trueloc)):
        	trueloc[i][0] -= offset[i]

	points = nearest(trueloc, waypoints)

	for i in range(5):
		pose[i].pose.position.x = points[i][0] + offset[i] 
	    	pose[i].pose.position.y = points[i][1] 
		pose[i].pose.position.z = z
	return pose


