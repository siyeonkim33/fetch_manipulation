# Fetch Robot Manipulation test 
A guideline for Fetch robot under the simulation and real-world.

Tested on Ubuntu 18.04 + Ros Melodic

## Build and Compile
1. Clone this repository:
~~~
cd ~/Desktop
git clone https://github.com/siyeonkim33/fetch_ws.git
~~~
2. Build the workspace:
~~~
cd ~/Desktop/fetch_ws
catkin_make
~~~

## Execution

### Gazebo world
Before opening gazebo world, there might be several minor errors.

1. Error in REST request

: Open the configuration file.
~~~
sudo gedit ~/.ignition/fuel/config.yaml 
~~~
: Change the line 6 from **url: https://api.ignitionfuel.org** to **url: https://api.ignitionrobotics.org**

### MoveIt!
Open the visualization tool *Rviz* and start *move_group* for Fetch robot. 
With the execution of ros launch file below, it will be able to run *Planning Scene Interface* on Rviz. Also, you can check whether the remote PC is successfully communicating with Fetch robot via turning-on the interactive marker on Rviz.
~~~
roslaunch fetch_moveit_demo demo.launch # Turn-on Rviz and PlanningSceneInterface*
~~~
or
~~~
roslaunch fetch_moveit_demo move_group.launch # Only run the move_group node
~~~
### PoseCNN
~~~
roscd pose_cnn
./experiments/scripts/ros_ycb_object_test.sh {gpu_ids}
~~~
