const express = require('express');
const ROSLIB = require('roslib');
const http = require('http');
const socketio = require('socket.io');
const fs = require('fs');
const resizebase64 = require('resize-base64');  
const app = express();
const server = http.createServer(app);
const cv = require("@techstark/opencv-js");
const helmet  = require('helmet');
const io = socketio(server);

let message = null;

const listener = new ROSLIB.Topic({
  ros: new ROSLIB.Ros({
    url: 'ws://localhost:9090' // Replace with your ROS web socket URL
  }),
  name: '/diff_cont/cmd_vel_unstamped',
  messageType: 'geometry_msgs/Twist'
});

listener.subscribe((data) => {
  console.log(`Received message: ${data}`);
  
  io.emit('message', data); // Send the message to all connected clients
});





// take image here to push socket
// npm install @u4/opencv4nodejs
const imageListener = new ROSLIB.Topic({
    ros: new ROSLIB.Ros({
      url: 'ws://localhost:9090' // Replace with your ROS web socket URL
    }),
    name: '/camera/image_raw',
    messageType: 'sensor_msgs/msg/Image'
  });
  imageListener.subscribe((message) => {

    io.emit('image', message);}
    
  );





io.on('connection', (socket) => {
  console.log('A client connected');
  if (message) {
    socket.emit('message', message); // Send the last received message to the new client
  } else {
    socket.emit('message', 'No message received yet');
  }
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/test.html');
});
app.use(helmet())

server.listen(3000, () => {
  console.log('Server listening on port 3000');
});

