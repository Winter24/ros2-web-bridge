# ros2-web-bridge 
This project is a web app that allow to control the robot using SLAM_Toolbox and Nav2 (ROS2 Foxy).
I havent test it on latest distro of ROS2 but you can use it for your project as a reference if you want  

Still updating if i have free time ;)

<p align="center">
  <img src="" alt="Centered image" width="600" height="400" />
  <img src="" alt="Centered image" width="600" height="400" />
</p>

## Supported Clients
A client is a program that communicates with ros2-web-bridge using its JSON API. Clients include:

* [roslibjs](https://github.com/RobotWebTools/roslibjs) - A JavaScript API, which communicates with ros2-web-bridge over WebSockets.

## Install
1. Prepare for ROS 2
    Please reference the [documentation](https://index.ros.org/doc/ros2/Installation/) to install ROS 2.
2. Install `Node.js`
    You can install Node.js:
    * Download from Node.js offical [website](https://nodejs.org/en/), and install it.
    * Use the Node Version Manager ([nvm](https://github.com/creationix/nvm)) to install it.
3. Clone and install dependencies
    Note that a ROS 2 installation has to be sourced before installing dependencies.
    ```bash
    $ git clone https://github.com/RobotWebTools/ros2-web-bridge.git
    $ cd ros2-web-bridge
    $ source /opt/ros/$DISTRO/setup.sh  # or a source installation
    $ npm install
    ```

## Run Examples
Run your robot launch file first then run the robot_pose_publisher then run the app

## Compability with rosbridge v2.0 protocol
* Subscribe to a topic.
  ```JavaScript
  // Define a topic with its type.
  var example = new ROSLIB.Topic({
    ros : ros,
    name : '/example_topic',
    messageType : 'std_msgs/String'
  });

  // Subscribe to a topic.
  example.subscribe(function(message) {
    console.log(`Receive message: ${message}`);
  });
  ```
Still updating

