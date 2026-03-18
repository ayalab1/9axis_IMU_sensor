/* Code to read data from the MPU9250 using a arduino mega
 *  Hardware setup:
 *  sensor -> arduino pin
 *  SCL    -> 21
 *  SDA    -> 20
 *  VCC    -> 3.3V
 *  GND    -> GND
 *  It's based on Hedieki and 's code (which also includes some calibration functions)
 *  https://github.com/hideakitai/MPU9250.git and https://github.com/arnefmeyer/IMUReaderPlugin.git
 */

#include "MPU9250.h"
// processing status
int status;
int triggerPin = 13;
MPU9250 mpu;

struct GeoData
{
  char beginning;
  float AccX;
  float AccY;
  float AccZ;
  float GyroX;
  float GyroY;
  float GyroZ;
  float MagX;
  float MagY;
  float MagZ;
  float Roll;
  float Pitch;
  float Yaw;
  unsigned long ts;
  unsigned long counter;
  };
GeoData geodata;
void setup() {
  // put your setup code here, to run once:

    Serial.begin(115200);
    Wire.begin();
    delay(2000);
    if (!mpu.setup(0x68)) {  // change to your own address
        while (1) {
            Serial.println("MPU connection failed. Please check your connection with `connection_check` example.");
            delay(5000);
        }
    }
    geodata.AccX = 0;// mpu.getAccX(); //
    geodata.AccY =0; //mpu.getAccY(); //
    geodata.AccZ = 0;//mpu.getAccZ(); //

    // gyroscope data (convert to dps)
    geodata.GyroX = 0;
    geodata.GyroY= 0;
    geodata.GyroZ = 0;

    // magnetometer data (convert to milliGauss)
    geodata.MagX  =0;
    geodata.MagY = 0;
    geodata.MagZ =0;
    // Sensor position
    // Yaw is the angle between Sensor x-axis and Earth magnetic North (or true North if corrected for local declination, looking down on the sensor positive yaw is counterclockwise.
    // Pitch is angle between sensor x-axis and Earth ground plane, toward the Earth is positive, up toward the sky is negative.
    // Roll is angle between sensor y-axis and Earth ground plane, y-axis up is positive roll.

    geodata.Roll = 0;
    geodata.Pitch = 0;
    geodata.Yaw = 0;
geodata.beginning='a';
geodata.ts=0;
geodata.counter=0;
//ephys TTL
  pinMode(triggerPin, OUTPUT);
  digitalWrite(triggerPin, LOW);


}

void loop() {
  // put your main code here, to run repeatedly:
  geodata.ts= millis();
if (mpu.update())
{
    //convert to mg per second
    geodata.AccX = mpu.getAccX(); //
    geodata.AccY =mpu.getAccY(); //
    geodata.AccZ = mpu.getAccZ(); //

    // gyroscope data (convert to dps)
    geodata.GyroX = mpu.getGyroX();
    geodata.GyroY= mpu.getGyroY();
    geodata.GyroZ = mpu.getGyroZ();

    // magnetometer data (convert to milliGauss)
    geodata.MagX  = mpu.getMagX();
    geodata.MagY = mpu.getMagY();
    geodata.MagZ = mpu.getMagZ();
    // Sensor position
    // Yaw is the angle between Sensor x-axis and Earth magnetic North (or true North if corrected for local declination, looking down on the sensor positive yaw is counterclockwise.
    // Pitch is angle between sensor x-axis and Earth ground plane, toward the Earth is positive, up toward the sky is negative.
    // Roll is angle between sensor y-axis and Earth ground plane, y-axis up is positive roll.

    geodata.Roll = mpu.getRoll();
    geodata.Pitch = mpu.getPitch();
    geodata.Yaw = mpu.getYaw();
}
    if(Serial.available()){
    byte a = Serial.read();
    if(a == 'h'){
   Serial.write((byte *) &geodata, (14*4+1));
   digitalWrite(triggerPin, HIGH);
   geodata.counter++;
   delay(1);
   digitalWrite(triggerPin, LOW);
    }
    if(a=='c')
    {
      Serial.println("Accel Gyro calibration will start in 5sec.");
    Serial.println("Please leave the device still on the flat plane.");
    mpu.verbose(true);
    delay(5000);
    mpu.calibrateAccelGyro();
    Serial.println("Mag calibration will start in 5sec.");
    Serial.println("Please Wave device in a figure eight until done.");
    delay(5000);
    mpu.calibrateMag();
    Serial.println(">"
    +String(mpu.getAccBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY)+","
    +String(mpu.getAccBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY)+","
    +String(mpu.getAccBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY)+","
    +String(mpu.getGyroBiasX() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY)+","
    +String(mpu.getGyroBiasY() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY)+","
    +String(mpu.getGyroBiasZ() * 1000.f / (float)MPU9250::CALIB_ACCEL_SENSITIVITY)+","
    +String(mpu.getMagBiasX())+","
    +String(mpu.getMagBiasY())+","
    +String(mpu.getMagBiasZ())+","
    +String(mpu.getMagScaleX())+","
    +String(mpu.getMagScaleY())+","
    +String(mpu.getMagScaleZ())
    +"<");
    mpu.verbose(false);
      }
    }
}
