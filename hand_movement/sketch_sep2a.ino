#include <Wire.h>
#include <MPU6050_light.h>


MPU6050 mpu(Wire);
float roll, pitch, yaw;


void setup() {
  Serial.begin(115200);   // Start serial communication
  Wire.begin();           // Start I2C communication
  mpu.begin();            // Initialize the MPU6050
  mpu.calcOffsets();      // Calibrate: keep sensor STILL during this!
}


void loop() {
  mpu.update();           // Read latest sensor values
  roll  = mpu.getAngleX();
  pitch = mpu.getAngleY();
  yaw   = mpu.getAngleZ();


  // Send values over USB as: roll,pitch,yaw
  Serial.print(roll);  Serial.print(',');
  Serial.print(pitch); Serial.print(',');
  Serial.println(yaw); // println adds newline at end
  delay(10);            // Wait 10ms before next reading
}
