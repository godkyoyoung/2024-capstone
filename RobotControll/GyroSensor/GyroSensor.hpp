#include <Wire.h>
#include "MPU6050/MPU6050.h"

class GyroSensor {
  private:
    float accelX_g;
    float accelY_g;
    float accelZ_g;
    float gyroX_degPerSec;
    float gyroY_degPerSec;
    float gyroZ_degPerSec;
    MPU6050 mpu;
  public:
    GyroSensor();
    void getSensorValue();
    float* getAccel_g();
    float* getGyro_degPerSec();

    float getAccelX_g();
    float getAccelY_g();
    float getAccelZ_g();

    float getGyroX_degPerSec();
    float getGyroY_degPerSec();
    float getGyroZ_degPerSec();
}

// MPU6050 mpu;

// // void setup() {
// //   Serial.begin(9600);
  
// //   // MPU-6050 초기화
// //   mpu.initialize();
  
// //   // 가속도 센서 범위 설정 (기본값: ±2g)
// //   mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
  
// //   // 각속도 센서 범위 설정 (기본값: ±250°/s)
// //   mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);
  
// //   // DMP 시작 (Digital Motion Processor)
// //   mpu.dmpInitialize();
// //   mpu.setDMPEnabled(true);
  
// //   // FIFO(First In First Out) 버퍼 비우기
// //   mpu.resetFIFO();
// // }

// void loop() {
//   // MPU 데이터 갱신 여부 확인
//   if (mpu.dmpGetCurrentFIFOPacket()) {
//     // 가속도(x, y, z) 및 각속도(x, y, z) 값을 읽어옴
//     int16_t accelX = mpu.getAccelerationX();
//     int16_t accelY = mpu.getAccelerationY();
//     int16_t accelZ = mpu.getAccelerationZ();
//     int16_t gyroX = mpu.getRotationX();
//     int16_t gyroY = mpu.getRotationY();
//     int16_t gyroZ = mpu.getRotationZ();

//     // 변환된 값을 계산하여 출력
//     this->accelX_g = accelX / 16384.0;  // 가속도의 단위: g (1g = 9.8 m/s^2)
//     this->accelY_g = accelY / 16384.0;
//     this->accelZ_g = accelZ / 16384.0;
//     this->gyroX_degPerSec = gyroX / 131.0;  // 각속도의 단위: °/s
//     this->gyroY_degPerSec = gyroY / 131.0;
//     this->gyroZ_degPerSec = gyroZ / 131.0;
//   }
// }