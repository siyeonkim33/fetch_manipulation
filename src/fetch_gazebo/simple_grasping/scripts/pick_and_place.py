#!/usr/bin/env python

import argparse
import copy
import math
import sys
import struct
import ctypes

import rospy
import actionlib
from moveit_python import *
from moveit_python.geometry import rotate_pose_msg_by_euler_angles

from grasping_msgs.msg import *
from moveit_msgs.msg import MoveItErrorCodes, PlaceLocation

import sensor_msgs.point_cloud2 as pc2

joint_names = ["shoulder_pan_joint", "shoulder_lift_joint", "upperarm_roll_joint",
    "elbow_flex_joint", "forearm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"]
ready_pose = [-1.393150, -0.103543, 0, -1.608378, -0.458660, -0.1, -2.611218]

def move_to_ready(interface):
   result = interface.moveToJointPosition(joint_names, ready_pose)
   if result.error_code.val != 1:
       rospy.sleep(1.0)
       rospy.logerr("Move arm to ready position failed, trying again...")
       result = interface.moveToJointPosition(joint_names, ready_pose, 0.02)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Simple demo of pick and place")
    parser.add_argument("--objects", help="Just do object perception", action="store_true")
    parser.add_argument("--all", help="Just do object perception, but insert all objects", action="store_true")
    parser.add_argument("--once", help="Run once.", action="store_true")
    parser.add_argument("--ready", help="Move the arm to the ready position.", action="store_true")
    parser.add_argument("--plan", help="Only do planning, no execution", action="store_true")
    parser.add_argument("--x", help="Recommended x offset, how far out an object should roughly be.", type=float, default=0.5)
    args, unknown = parser.parse_known_args()

    rospy.init_node("pick_and_place_demo")
    move_group = MoveGroupInterface("arm", "base_link", plan_only = args.plan)

    print("WOW")
    # if all we want to do is prepare the arm, do it now
    if args.ready:
        move_to_ready(move_group)
        exit(0)

    scene = PlanningSceneInterface("base_link")
    pickplace = PickPlaceInterface("arm", "gripper", plan_only = args.plan, verbose = True)

    rospy.loginfo("Connecting to basic_grasping_perception/find_objects...")
    find_objects = actionlib.SimpleActionClient("basic_grasping_perception/find_objects", FindGraspableObjectsAction)
    find_objects.wait_for_server()
    rospy.loginfo("...connected")

    while not rospy.is_shutdown():
        goal = FindGraspableObjectsGoal()
        goal.plan_grasps = True
        find_objects.send_goal(goal)
        find_objects.wait_for_result(rospy.Duration(5.0))
        find_result = find_objects.get_result()

        rospy.loginfo("Found %d objects" % len(find_result.objects))


        # remove all previous objects
        for name in scene.getKnownCollisionObjects():
            scene.removeCollisionObject(name, False)
        for name in scene.getKnownAttachedObjects():
            scene.removeAttachedObject(name, False)
        scene.waitForSync()
        # clear colors
        scene._colors = dict()

        # insert objects, find the one to grasp
        the_object = None
        the_object_dist = 0.35
        count = -1
        for obj in find_result.objects:
            print("%s block is added" % obj.object.properties[0].name)

            count += 1
            scene.addSolidPrimitive("%s_%d"%(obj.object.properties[0].name, count),
                                    obj.object.primitives[0],
                                    obj.object.primitive_poses[0])
            # object must have usable grasps
            if len(obj.grasps) < 1:
                continue
            # choose object in front of robot
            dx = obj.object.primitive_poses[0].position.x - args.x
            dy = obj.object.primitive_poses[0].position.y
            d = math.sqrt((dx * dx) + (dy * dy))
            if d < the_object_dist:
                the_object_dist = d
                the_object = count

        if the_object == None:
            rospy.logerr("Nothing to grasp! try again...")
            continue

        # insert table
        for obj in find_result.support_surfaces:
            # extend surface to floor
            height = obj.primitive_poses[0].position.z
            obj.primitives[0].dimensions = [obj.primitives[0].dimensions[0] + 0.2,
                                            2.0, # make table wider
                                            obj.primitives[0].dimensions[2] + height]
            obj.primitive_poses[0].position.z += -height/2.0

            # add to scene
            scene.addSolidPrimitive(obj.name,
                                    obj.primitives[0],
                                    obj.primitive_poses[0])

        obj_name = "%s%d"%(find_result.objects[the_object].object.properties[0].name,the_object)

        # sync
        scene.waitForSync()

        # set color of object we are grabbing
        scene.setColor(obj_name, 223.0/256.0, 90.0/256.0, 12.0/256.0)  # orange
        scene.setColor(find_result.objects[the_object].object.support_surface, 0, 0, 0)  # black
        scene.sendColors()

        # exit now if we are just doing object update
        if args.objects:
            if args.once:
                exit(0)
            else:
                continue

        # get grasps (we checked that they exist above)
        grasps = find_result.objects[the_object].grasps
        support_surface = find_result.objects[the_object].object.support_surface

        # call move_group to pick the object
        rospy.loginfo("Beginning to pick.")
        success, pick_result = pickplace.pick_with_retry(obj_name, grasps, support_name=support_surface, scene=scene)
        if not success:
            exit(-1)

        # create a set of place locations for the cube
        places = list()
        l = PlaceLocation()
        l.place_pose.pose = find_result.objects[the_object].object.primitive_poses[0]
        l.place_pose.header.frame_id = find_result.objects[the_object].object.header.frame_id
        # invert the y of the pose
        if (obj_name.find("red") > 0):
            print("find red")
            l.place_pose.pose.position.x = 0.7
            l.place_pose.pose.position.y = -0.4
            l.place_pose.pose.position.z = 1
        else:
            print("find blue")
            l.place_pose.pose.position.x = 0.7
            l.place_pose.pose.position.y = 0.4
            l.place_pose.pose.position.z = 1

        # l.place_pose.pose.position.y = -l.place_pose.pose.position.y
        # copy the posture, approach and retreat from the grasp used
        l.post_place_posture = pick_result.grasp.pre_grasp_posture
        l.pre_place_approach = pick_result.grasp.pre_grasp_approach
        l.post_place_retreat = pick_result.grasp.post_grasp_retreat
        places.append(copy.deepcopy(l))
        # create another several places, rotate each by 90 degrees in yaw direction
        l.place_pose.pose = rotate_pose_msg_by_euler_angles(l.place_pose.pose, 0, 0, 1.57)
        places.append(copy.deepcopy(l))
        l.place_pose.pose = rotate_pose_msg_by_euler_angles(l.place_pose.pose, 0, 0, 1.57)
        places.append(copy.deepcopy(l))
        l.place_pose.pose = rotate_pose_msg_by_euler_angles(l.place_pose.pose, 0, 0, 1.57)
        places.append(copy.deepcopy(l))

        # drop it like it's hot
        rospy.loginfo("Beginning to place.")
        while not rospy.is_shutdown():
            # can't fail here or moveit needs to be restarted
            success, place_result = pickplace.place_with_retry(obj_name, places, support_name=support_surface, scene=scene)
            if success:
                break

        # place arm back at side
        move_to_ready(move_group)
        rospy.loginfo("Ready...")

        # rinse and repeat
        if args.once:
            exit(0)

