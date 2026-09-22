#include <Wire.h>
#include <MPU6050_light.h>


MPU6050 mpu(Wire);
float roll, pitch;


void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu.begin();
  mpu.calcOffsets();  // Keep sensor still during calibration!
}


void loop() {
  mpu.update();
  roll  = mpu.getAngleX();
  pitch = mpu.getAngleY();


  // Check tilt and send direction over serial
  if      (pitch >  20) Serial.println("UP");
  else if (pitch < -20) Serial.println("DOWN");
  else if (roll  >  20) Serial.println("RIGHT");
  else if (roll  < -20) Serial.println("LEFT");
  else                  Serial.println("NONE");


  delay(100);  // 100ms between readings (10 times per second)
}
