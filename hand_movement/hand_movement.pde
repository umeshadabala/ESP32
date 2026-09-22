import processing.serial.*;
import processing.opengl.*;

Serial myPort;

float roll = 0;
float pitch = 0;
float yaw = 0;

// macOS serial port
String portName = "/dev/tty.usbserial-0001";

void setup() {
  size(800, 600, P3D);

  println("Available serial ports:");
  println(Serial.list());

  myPort = new Serial(this, portName, 115200);
  myPort.bufferUntil('\n');
}

void draw() {
  background(50);

  // Enable 3D lighting
  lights();

  // Move object to center
  translate(width / 2, height / 2, 0);

  // Apply MPU6050 orientation
  rotateY(radians(yaw));
  rotateX(radians(pitch));
  rotateZ(radians(roll));

  // Palm
  fill(255, 220, 180);
  box(80, 100, 30);

  // Thumb
  pushMatrix();
  translate(40, -20, 0);
  rotateZ(radians(30));
  box(25, 60, 25);
  popMatrix();

  // Index finger
  pushMatrix();
  translate(-30, -50, 0);
  box(20, 70, 20);
  popMatrix();

  // Middle finger
  pushMatrix();
  translate(0, -55, 0);
  box(20, 80, 20);
  popMatrix();

  // Ring finger
  pushMatrix();
  translate(30, -50, 0);
  box(20, 75, 20);
  popMatrix();
}

void serialEvent(Serial myPort) {
  String data = myPort.readStringUntil('\n');

  if (data != null) {
    data = trim(data);

    String[] angles = split(data, ',');

    if (angles.length == 3) {
      try {
        roll = float(angles[0]);
        pitch = float(angles[1]);
        yaw = float(angles[2]);

        println(
          "Roll: " + roll +
          "  Pitch: " + pitch +
          "  Yaw: " + yaw
        );
      }
      catch (Exception e) {
        println("Invalid serial data: " + data);
      }
    }
  }
}
