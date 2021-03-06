#!/usr/bin/env python
import sys
import copy
import os
import actionlib
import rospy
import rospkg
import time
import moveit_commander

from math import sin, cos, pi
from moveit_python import (MoveGroupInterface, PlanningSceneInterface, PickPlaceInterface)
from moveit_python.geometry import rotate_pose_msg_by_euler_angles

from control_msgs.msg import FollowJointTrajectoryAction, FollowJointTrajectoryGoal, GripperCommandAction, GripperCommandGoal
from control_msgs.msg import PointHeadAction, PointHeadGoal
from grasping_msgs.msg import FindGraspableObjectsAction, FindGraspableObjectsGoal

from geometry_msgs.msg import PoseStamped
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from moveit_msgs.msg import PlaceLocation, MoveItErrorCodes, Grasp
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from gazebo_msgs.srv import (
    SpawnModel,
    DeleteModel,
)

from geometry_msgs.msg import (
    PoseStamped,
    Pose,
    Point,
    Quaternion,
)


# Point the head using controller
class PointHeadClient(object):

    def __init__(self):
        self.client = actionlib.SimpleActionClient("head_controller/point_head", PointHeadAction)
        rospy.loginfo("Waiting for head_controller...")
        self.client.wait_for_server()

    def look_at(self, x, y, z, frame, duration=1.0):
        goal = PointHeadGoal()
        goal.target.header.stamp = rospy.Time.now()
        goal.target.header.frame_id = frame
        goal.target.point.x = x
        goal.target.point.y = y
        goal.target.point.z = z
        goal.min_duration = rospy.Duration(duration)
        self.client.send_goal(goal)
        self.client.wait_for_result()

# Tools for grasping
class GraspingClient(object):

    def __init__(self):
        self.scene = PlanningSceneInterface("base_link")
        self.pickplace = PickPlaceInterface("arm", "gripper", verbose=True)
        self.move_group = MoveGroupInterface("arm", "base_link")

        find_topic = "basic_grasping_perception/find_objects"
        rospy.loginfo("Waiting for %s..." % find_topic)
        self.find_client = actionlib.SimpleActionClient(find_topic, FindGraspableObjectsAction)
        self.find_client.wait_for_server()

    def updateScene(self):
        # find objects
        goal = FindGraspableObjectsGoal()
        goal.plan_grasps = True
        self.find_client.send_goal(goal)
        self.find_client.wait_for_result(rospy.Duration(5.0))
        find_result = self.find_client.get_result()

        rospy.loginfo("Found %d objects" % len(find_result.objects))

        # remove previous objects
        #for name in self.scene.getKnownCollisionObjects():
        #    self.scene.removeCollisionObject(name, False)
        #for name in self.scene.getKnownAttachedObjects():
        #    self.scene.removeAttachedObject(name, False)
        self.scene.waitForSync()

        # insert objects to scene
        objects = list()
        idx = -1
        for obj in find_result.objects:
            idx += 1

            #obj.object.name = find_result.objects[idx].name -> 'GraspableObject' object has no attribute 'name
            obj.object.name = "obj%d"%idx
            self.scene.addSolidPrimitive(obj.object.name, obj.object.primitives[0], obj.object.primitive_poses[0], use_service=False)
            if obj.object.primitive_poses[0].position.x < 1.3: #< 0.85:
                objects.append([obj, obj.object.primitive_poses[0].position.y]) ##should be it's goal position,,,
                #objects.append([obj, obj.object.primitive_poses[0].position.z])

        #for obj in find_result.support_surfaces:
        #    # extend surface to floor, and make wider since we have narrow field of view
        #    height = obj.primitive_poses[0].position.z
        #    obj.primitives[0].dimensions = [obj.primitives[0].dimensions[0], 1.5,  # wider
        #                                    obj.primitives[0].dimensions[2] + height]
        #    obj.primitive_poses[0].position.z += -height/2.0

        #    # add to scene
        #    self.scene.addSolidPrimitive(obj.name, obj.primitives[0], obj.primitive_poses[0])
        self.scene.waitForSync()

        # store for grasping
        self.surfaces = find_result.support_surfaces

        # store graspable objects by Z -> y
        objects.sort(key=lambda object: object[1])
        #objects.reverse()
        self.objects = [object[0] for object in objects]

#obj0_goal = (0, Pose(position=Point(x=1.114, y= -0.858, z= 0.65), orientation=Quaternion(x=0, y=0, z=0, w=1)))

    def getGraspableObject(self, goal_obj_x, goal_obj_y):
        graspable = None
        for obj in self.objects:
            # # need grasps
            # if len(obj.grasps) < 1:
            #     continue
            # # check size
            # if obj.object.primitives[0].dimensions[0] < 0.03 or \
            #    obj.object.primitives[0].dimensions[0] > 0.25 or \
            #    obj.object.primitives[0].dimensions[0] < 0.03 or \
            #    obj.object.primitives[0].dimensions[0] > 0.25 or \
            #    obj.object.primitives[0].dimensions[0] < 0.03 or \
            #    obj.object.primitives[0].dimensions[0] > 0.25:
            #     continue
            # # has to be on table
            # if obj.object.primitive_poses[0].position.z < 0.4:
            #     continue
            # if obj.object.primitive_poses[0].position.x < 0.3:
            #     continue
            # # get goal object
            # if ( abs(obj.object.primitive_poses[0].position.x - goal_obj_x) > 0.03):
            #     continue
            # if ( abs(obj.object.primitive_poses[0].position.y - goal_obj_y) > 0.03):
            #     continue

            # print("**************************************Object Name: ", obj.object.name)
            # print("Object Pose: ", obj.object.primitive_poses[0], obj.object.primitives[0])
            # return obj.object, obj.grasps
            retrun obj.object
        # nothing detected
        # return None, None
        return None

    def getSupportSurface(self, name):
        for surface in self.support_surfaces:
            if surface.name == name:
                return surface
        return None

    def getPlaceLocation(self):
        pass

    # def pick(self, block, grasps):
    #     ## (self, name, grasps, retries=5, scene=None,)
    #     success, pick_result = self.pickplace.pick_with_retry(block.name, grasps, support_name=block.support_surface, scene=self.scene)
    #     self.pick_result = pick_result
    #     return success

    def pick(self, block, close_gripper_to=0.02, retry=1, tolerance=0.01, x_diff_pick=-0.01, z_diff_pick=0.1, x_diff_grasp=-0.01, z_diff_grasp=0.01):
        self.gripper_client.fully_open_gripper() ## open gripper

        #===== self.angle ====#
        angle_tmp = self.angle
        input_retry = retry
        success = False

        while angle_tmp <= self.angle_max and not success:
            radian = (angle_tmp / 2.0) * (pi / 180.0)    ## convert degree to radian
            rot_orientation = Quaternion(0.0, sin(radian), 0.0, cos(radian))

            ## orientation & quarternion
            obj_ori = obj.primitive_poses[0].orientation
            obj_quat = [obj_ori.x, obj_ori.y, obj_ori.z, obj_ori.w]

            ## rotations (roll, pitch, yaw)
            roll, pitch, yaw = transformations.euler_from_quaternion(obj_quat)

            ### extract the yaw orientation from the object 
            yaw_quat = transformations.quaternion_from_euler(0.0, 0.0, yaw)
            yaw_orientation = Quaternion(yaw_quat[0], yaw_quat[1], yaw_quat[2], yaw_quat[3])

            # multiply the previous pitch orientation that the gripper is goring to rotate
            ## The new orientation will be the orientation of the gripper link
            gripper_orientation = self.quaternion_multiply(yaw_orientation, rot_orientation)


            # The position of the gripper link will be the position of the cube \\
            # plus x_diff_pick in gripper link x axis direction and plus z_diff_pick in the gripper link z axis direction

            # The reason to do this is that if the we plan the gripper to the exact object position, the grippers might hit the object due to the observation errors.
            first_poseStamped = self.make_poseStamped("base_link", obj.primitive_poses[0], gripper_orientation)
            first_poseStamped.pose.position.x += x_diff_pick     
            first_poseStamped.pose.position.z += z_diff_pick

            while retry > 0:
                move_pose_result = self.move_group.moveToPose(first_poseStamped, "gripper_link", tolerance=tolerance, PLAN_ONLY=True)
                rospy.sleep(1.0)
                if move_pose_result.error_code.val == MoveItErrorCodes.SUCCESS:
                    success = True
                    break
                else:
                    if move_pose_result.error_code.val == MoveItErrorCodes.NO_IK_SOLUTION:
                        rospy.loginfo("no valid IK found")               
                    rospy.loginfo(move_pose_result.error_code.val)
                retry -= 1
            angle_tmp += self.angle_step
            retry = input_retry
        if retry == 0:
            return False

        success = False
        curr_retry = retry
        while angle_tmp  <= 90 and not success:
            radian = (angle_tmp  / 2) * (pi / 180)
            rot_orientation = Quaternion(0.0, sin(radian), 0.0, cos(radian))

            gripper_orientation = self.quaternion_multiply(yaw_orientation, rot_orientation)
            gripper_pose_stamped = self.make_poseStamped("base_link", obj.primitive_poses[0], gripper_orientation)
            gripper_pose_stamped.pose.position.z += z_diff_grasp
            gripper_pose_stamped.pose.position.x += x_diff_grasp

            while curr_retry > 0:
                move_pose_result = self.move_group.moveToPose(gripper_pose_stamped, "gripper_link", tolerance=tolerance)
                rospy.sleep(1.0)
                if move_pose_result.error_code.val == MoveItErrorCodes.SUCCESS:
                    success = True
                    break
                else:
                    if move_pose_result.error_code.val == MoveItErrorCodes.NO_IK_SOLUTION:
                        rospy.loginfo("no valid IK found")      
                    rospy.loginfo(move_pose_result.error_code.val)
                curr_retry -= 1
            angle_tmp  += self.angle_step
            curr_retry = retry
            rospy.loginfo("closing the gripper")
            self.makeAttach(obj)
            self.gripper_client.close_gripper_to(close_gripper_to)
        if curr_retry == 0:
            return False
        rospy.loginfo("done picking")
        return True

    def place(self, block, pose_stamped):
        places = list()
        l = PlaceLocation()
        l.place_pose.pose = pose_stamped.pose
        #l.place_pose.pose.position.x = 0.6
        #l.place_pose.pose.position.y= -0.15
        #l.place_pose.pose.position.z= 0.65
        l.place_pose.header.frame_id = pose_stamped.header.frame_id

        # copy the posture, approach and retreat from the grasp used
        l.post_place_posture = self.pick_result.grasp.pre_grasp_posture
        l.pre_place_approach = self.pick_result.grasp.pre_grasp_approach
        l.post_place_retreat = self.pick_result.grasp.post_grasp_retreat
        places.append(copy.deepcopy(l))
        # create another several places, rotate each by 360/m degrees in yaw direction
        m = 16 # number of possible place poses
        pi = 3.141592653589
        for i in range(0, m-1):
            #l.place_pose.pose = rotate_pose_msg_by_euler_angles(l.place_pose.pose, 0, 0, 2 * pi / m)
            places.append(copy.deepcopy(l))

        success, place_result = self.pickplace.place_with_retry(block.name, places, scene=self.scene)
        return success

    ## tuck pose
    def tuck(self):
        joints = ["shoulder_pan_joint", "shoulder_lift_joint", "upperarm_roll_joint",
                  "elbow_flex_joint", "forearm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"]
        pose = [1.32, 1.40, -0.2, 1.72, 0.0, 1.66, 0.0]
        while not rospy.is_shutdown():
            result = self.move_group.moveToJointPosition(joints, pose, 0.02)
            if result.error_code.val == MoveItErrorCodes.SUCCESS:
                return

    # stow pose
    def stow(self):
        joints = ["shoulder_pan_joint", "shoulder_lift_joint", "upperarm_roll_joint",
                  "elbow_flex_joint", "forearm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"]
        pose = [1.32, 0.7, 0.0, -2.0, 0.0, -0.57, 0.0]
        #pose = [-1.60, -1.10, -1.20, -1.50, 0.0, -1.51, 0.0]
        while not rospy.is_shutdown():
            result = self.move_group.moveToJointPosition(joints, pose, 0.02)
            if result.error_code.val == MoveItErrorCodes.SUCCESS:
                return

    # intermediate stow pose
    def intermediate_stow(self):
        joints = ["shoulder_pan_joint", "shoulder_lift_joint", "upperarm_roll_joint",
                  "elbow_flex_joint", "forearm_roll_joint", "wrist_flex_joint", "wrist_roll_joint"]
        pose = [0.7, -0.3, 0.0, -0.3, 0.0, -0.57, 0.0]
        while not rospy.is_shutdown():
            result = self.move_group.moveToJointPosition(joints, pose, 0.02)
            if result.error_code.val == MoveItErrorCodes.SUCCESS:
                return

#===================================================================================
def spawn_gazebo_model(model_path, model_name, model_pose, reference_frame="world"):
  model_xml = ''
  with open(model_path, "r") as model_file:
    model_xml = model_file.read().replace('\n', '')
  rospy.wait_for_service('/gazebo/spawn_urdf_model')
  try:
    spawn_urdf = rospy.ServiceProxy('/gazebo/spawn_urdf_model', SpawnModel)
    resp_urdf = spawn_urdf(model_name, model_xml, "/", model_pose, reference_frame)
  except rospy.ServiceException, e:
    rospy.logerr("Spawn URDF service call failed: {0}".format(e))

def delete_gazebo_model(models):
  """
  Delete model in gazebo
  """
  try:
    delete_model = rospy.ServiceProxy('/gazebo/delete_model', DeleteModel)
    for a_model in models:
      resp_delete = delete_model(a_model)
  except rospy.ServiceException, e:
    rospy.loginfo("Delete Model service call failed: {0}".format(e))
#===================================================================================
if __name__ == "__main__":
    rospack = rospkg.RosPack()
    pack_path = rospack.get_path('fetch_goal_gnrt')
    rospy.init_node("demo") # Create a node

    # Make sure sim time is working
    while not rospy.Time.now():
        pass

    # Setup clients
    head_action = PointHeadClient()
    grasping_client = GraspingClient() # Control scene, robot, arm
    grasping_client.stow() # Go to a default pose
    cube_in_grapper = False

    init_pose = [
                # Pose(position=Point(x=0.8, y=-0.3, z=0.5)),
                # Pose(position=Point(x=0.8, y=-0.2,  z=0.5)),
                # Pose(position=Point(x=0.8, y=-0.1,  z=0.5)),
                # Pose(position=Point(x=0.8, y=-0,    z=0.5)),
                # Pose(position=Point(x=0.8, y=0.1,   z=0.5)),
                # Pose(position=Point(x=0.8, y=0.2,   z=0.5)),
                Pose(position=Point(x=0.8, y=0,   z=0.5))]

    # object goal info tuble: (index, Pose)
    obj0_goal = (0, Pose(position=Point(x=0.6, y= 0.1,  z= 0.5), orientation=Quaternion(x=0, y=0, z=0, w=1)))
    # obj1_goal = (1, Pose(position=Point(x=0.6, y= 0.3,  z= 0.5), orientation=Quaternion(x=0, y=0, z=0, w=1)))
    # obj2_goal = (2, Pose(position=Point(x=0.6, y= -0.2, z= 0.5),  orientation=Quaternion(x=0, y=0, z=0, w=1)))
    # obj3_goal = (3, Pose(position=Point(x=0.6, y= -0.1, z= 0.5), orientation=Quaternion(x=0, y=0, z=0, w=1)))
    # obj4_goal = (4, Pose(position=Point(x=0.6, y= 0,    z= 0.5), orientation=Quaternion(x=0, y=0, z=0, w=1)))
    # obj5_goal = (5, Pose(position=Point(x=0.6, y= 0.2,  z= 0.5), orientation=Quaternion(x=0, y=0, z=0, w=1)))
    # obj6_goal = (6, Pose(position=Point(x=0.6, y= -0.3, z= 0.5), orientation=Quaternion(x=0, y=0, z=0, w=1)))

    obj_goal = [obj0_goal]
    # obj_goal = [obj0_goal, obj1_goal, obj2_goal, obj3_goal, obj4_goal, obj5_goal, obj6_goal]


    sorted_obj_goal = sorted(obj_goal, key=lambda obj: (obj[1].position.y, -obj[1].position.x))

    object_no = 1
    for b in range(0, object_no): #generate block objects
        object_path = os.path.join(pack_path, 'models', 'cubes', 'red_cube.sdf')
        object_name = 'obj'+str(b)
        object_pose = init_pose[b]
        spawn_gazebo_model(object_path, object_name, object_pose)
        time.sleep(0.3)

    obj_i = -1
    while not rospy.is_shutdown():
        obj_i += 1
        head_action.look_at(1.2, 0.0, 0.0, "base_link")

        # Get block to pick
        fail_ct = 0
        while not rospy.is_shutdown() and not cube_in_grapper:
            rospy.loginfo("Picking object...")
            print("*******obj index: ", obj_i)
            grasping_client.updateScene()

            print("*******goal y index: ", sorted_obj_goal[obj_i][0])
            print("*******goal object y: ", init_pose[sorted_obj_goal[obj_i][0]].position.y)

            # cube, grasps = grasping_client.getGraspableObject(init_pose[sorted_obj_goal[obj_i][0]].position.x, init_pose[sorted_obj_goal[obj_i][0]].position.y)

            if cube == None:
                rospy.logwarn("Perception failed.")
                # grasping_client.intermediate_stow()
                grasping_client.stow()
                head_action.look_at(1.2, 0.0, 0.0, "base_link")
                continue

            # Pick the block
            if grasping_client.pick(cube):
                cube_in_grapper = True
                break
            print("Pick Success")
            rospy.logwarn("Grasping failed.")
            grasping_client.stow()
            if fail_ct > 15:
                fail_ct = 0
                break
            fail_ct += 1

        # Place the block
        while not rospy.is_shutdown() and cube_in_grapper:
            rospy.loginfo("Placing object...")
            pose = PoseStamped()
            pose.pose = cube.primitive_poses[0]
            pose.pose.position = sorted_obj_goal[obj_i][1].position
            pose.header.frame_id = cube.header.frame_id
            if grasping_client.place(cube, pose):
                cube_in_grapper = False
                break
            rospy.logwarn("Placing failed.")
            #grasping_client.intermediate_stow()
            #grasping_client.stow()
            if fail_ct > 15:
                fail_ct = 0
                break
            fail_ct += 1
        # Tuck the arm, lower the torso

#        obj_i += 1
        grasping_client.intermediate_stow()
        grasping_client.stow()
        rospy.loginfo("Finished")
        #torso_action.move_to([0.0, ])
