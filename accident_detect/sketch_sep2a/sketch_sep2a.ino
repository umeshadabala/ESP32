#include <Wire.h>
#include <MPU6050_light.h>


MPU6050 mpu(Wire);


// Threshold: how strong a jerk needs to be to count as accident
// 2.5 means 2.5 times normal gravity (9.8 m/s^2)
float JERK_THRESHOLD = 2.5;


// Cooldown: wait 3 seconds before detecting another accident
unsigned long lastAlertTime = 0;
unsigned long COOLDOWN_MS   = 3000;


void setup() {
  Serial.begin(115200);
  Wire.begin();
  mpu.begin();


  Serial.println("Calibrating... Keep sensor STILL!");
  mpu.calcOffsets();  // This takes about 3 seconds
  Serial.println("Calibration done. Ready to detect accidents.");
}


void loop() {
  mpu.update();


  // Read raw acceleration in each axis (in G units)
  float ax = mpu.getAccX();
  float ay = mpu.getAccY();
  float az = mpu.getAccZ();


  // Calculate total magnitude of acceleration
  float totalAcc = sqrt(ax*ax + ay*ay + az*az);


  // Print current acceleration for monitoring
  Serial.print("Accel: ");
  Serial.println(totalAcc);


  // Check if it is a strong jerk AND cooldown has passed
  unsigned long now = millis();
  if (totalAcc > JERK_THRESHOLD && (now - lastAlertTime) > COOLDOWN_MS) {
    lastAlertTime = now;
    Serial.println("================================");
    Serial.println(" ACCIDENT DETECTED! ALERT! ");
    Serial.print  (" Peak Acceleration: ");
    Serial.print  (totalAcc);
    Serial.println(" G");
    Serial.println("================================");
  }


  delay(50);  // Check 20 times per second
}
