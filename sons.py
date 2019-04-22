#!/usr/bin/env python

import rospy
from math import acos
from math import sqrt
from math import pi
from geometry_msgs.msg import PoseStamped

son_location = [[], []]

def pose_callback1(msg1):
   sp1 = [msg1.pose.position.x, msg1.pose.position.y, msg1.pose.position.z]
   son_location[0] = sp1
   
def pose_callback2(msg2):
   sp2 = [msg2.pose.position.x, msg2.pose.position.y, msg2.pose.position.z]
   son_location[1] = sp2

"""******************************************************************************************"""

"""get son information"""


def getSonPoseSubscriber(numson):
   # forming a son subscriber topic list
   sonSubTopic = []
   # uav1 is mom.
   for i in range(numson):
      topic = 'uav' + str(i+2) +'/mavros/local_position/pose'
      sonSubTopic.append(topic)
   
   # forming a son subscriber list
   sonPose = []
   sonsub1 = rospy.Subscriber(sonSubTopic[0], PoseStamped, pose_callback1)
   sonsub2 = rospy.Subscriber(sonSubTopic[1], PoseStamped, pose_callback2)

def getSonVector(momLoc, sonLoc, numberOfSons):
   sonVectorFromMom = []
   for i in range(len(sonLoc)):
      sonVec = []
      # x1-x2, y1-y2, z1-z2
      for j in range(len(sonLoc[i])):
         sonVec.append(momLoc[j] - sonLoc[i][j])
      sonVectorFromMom.append(sonVec)
   return sonVectorFromMom

def getSonPosePublisher(numberofSons):
   sonPubTopic = []
   for i in range(numberofSons):
      topic = 'uav' + str(i+2) +'/mavros/setpoint_position/local'
      sonPubTopic.append(topic)
   sonPublisher = []
   for i in range(numberofSons):
      sonpub = rospy.Publisher(sonPubTopic[i], PoseStamped, queue_size=10)
      sonPublisher.append(sonpub)
   return sonPublisher

"""def getSonVelPublisher(numberofSons):
   sonVelTopic = []
   for i in range(numberofSons):
      topic = 'uav' + str(i+1) + '/cmd_vel'
      sonVelTopic.append(topic)
   sonVelPub = []
   for i in range(numberofSons):
      sonvpub = rospy.Publisher(sonVelTopic[i], Twist, queue_size=10)
      sonVelPub.append(sonvpub)
   return sonVelPub"""

"""***********************************************************************************************************"""

"""calculate angle and distance"""

def norm(vector):
   l = 0
   for i in range(len(vector)):
      l += vector[i] ** 2
   return sqrt(l)

def dot_product(v,w):
   dp = 0
   for i in range(len(v)):
      dp += v[i] * w[i]
   return dp

def getSonDistanceFromMom(sonVector):
   distancelist = []
   for i in range(len(sonVector)):
      distancelist.append(getDistance(sonVector[i]))
   return distancelist

def getDistance(sonvector):
   squared = 0
   for i in range(len(sonvector)):
      squared += (sonvector[i]) ** 2 
   distance = sqrt(squared)
   return distance

def getSonAngleBetween(sonVector):
   angle = []
   rad = []
   for i in range(len(sonVector)):
      for j in range(len(sonVector)):
         denominator = norm(sonVector[i])*norm(sonVector[j])
         if i == 0 and (i != j) and (denominator != 0):
            cosx = dot_product(sonVector[i],sonVector[j]) / denominator
	    rad.append(acos(cosx))
	 if (i > 0) and (i > j) and (i < (len(sonVector) -1)) and (denominator != 0):
	    cosx = dot_product(sonVector[i],sonVector[j]) / denominator
	    rad.append(acos(cosx))
   for m in range(len(rad)):
      angle.append(rad[m] * 180 / pi)
   return angle

"""***********************************************************************************************************"""


def updateSonLocation(numberOfSons, momLocation):


   rate = rospy.Rate(50)

   # sons subscribers
   getSonPoseSubscriber(numberOfSons)

   # form vector from son to mom
   sonVector = getSonVector(momLocation, son_location, numberOfSons)
   # sons pose publishers list
   sonPosePublisher = getSonPosePublisher(numberOfSons)
   """# sons velocity publishers list
   sonVelPublisher = getSonVelPublisher(numberofSons)"""

   # son distance
   sv = []
   if len(son_location) != 0 and len(son_location[0]) != 0:
      for i in range(3):
         sv.append(son_location[0][i] - son_location[1][i])
      sonDistance = getDistance(sv)

   # make triangle shape
   # sonDistance = [distance of 12, 13, 14 ... 23, 24 ... 34, 35 ...]
   # sonAngle = [angle of 12, 13, 14 ... 23, 24 ... 34, 35 ... ]
   sonDistanceFromMom = getSonDistanceFromMom(sonVector)
   sonAngle = getSonAngleBetween(sonVector)
   sonPose = []
   for i in range(numberOfSons):
      # sonPose = [[pose of son_1], [pose of son_2]]
      sonPose.append(PoseStamped())
 
   if len(son_location[0]) != 0:
   # adjust location if z_mom - z_son 
      for i in range(len(son_location)):
         # to adjust z location
         if momLocation[2] != son_location[i][2] :
            sonPose[i].pose.position.z = momLocation[2]

         # to adjust y location
         if abs(son_location[i][1] - momLocation[1]) != 1:
	    sonPose[i].pose.position.y = momLocation[1] - 1

         # to adjust x location
         if abs(son_location[i][0] - momLocation[0]) != 0.5:
            if i == 0:
               sonPose[i].pose.position.x = momLocation[0] - 0.5
            elif i == 1:
               sonPose[i].pose.position.x = momLocation[0] + 0.5

         if sonDistance != 1:            
            if i == 0:
               sonPose[i].pose.position.x = sonPose[i].pose.position.x - 0.1
               sonPose[i].pose.position.y = sonPose[i].pose.position.y - 0.1
            elif i == 1:
               sonPose[i].pose.position.x = sonPose[i].pose.position.x + 0.1
               sonPose[i].pose.position.y = sonPose[i].pose.position.y + 0.1

         # to initialize change
         else: 
            sonPose[i].pose.position.x = momLocation[0]
            sonPose[i].pose.position.y = momLocation[1]

      for i in range(len(sonPosePublisher)):          
         sonPose[i].header.stamp = rospy.Time.now()
         sonPosePublisher[i].publish(sonPose[i])






### check the syntax of subscriber and publiser.
### use virtual structure or circle????

# find the centroid of a circle of some radius
# then assign each vehicle to the location where
# its location will be in a constant distance from centroid


# or set the formation as triangle first.
# let the mom be one of the vertices
# sons have to be in the same distance from mom
# perpendicular distance of baseline to mom will be set at constant value













