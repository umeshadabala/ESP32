#include <Wire.h>
#include <MPU6050_light.h>

MPU6050 mpu(Wire);

void setup() {
  Serial.begin(115200);
  Wire.begin();

  byte status = mpu.begin();

  if (status != 0) {
    Serial.println("MPU6050_ERROR");
    while (1);
  }

  delay(1000);
  mpu.calcOffsets();

  Serial.println("READY");
}

void loop() {
  mpu.update();

  Serial.print(mpu.getAccX());
  Serial.print(",");
  Serial.print(mpu.getAccY());
  Serial.print(",");
  Serial.print(mpu.getAccZ());
  Serial.print(",");
  Serial.print(mpu.getGyroX());
  Serial.print(",");
  Serial.print(mpu.getGyroY());
  Serial.print(",");
  Serial.println(mpu.getGyroZ());

  delay(10);
}