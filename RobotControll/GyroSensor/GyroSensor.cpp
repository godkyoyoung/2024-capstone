#include "GyroSensor.hpp"

GyroSensor::setup() {
  // MPU-6050 초기화
  this->mpu.initialize();
  
  // 가속도 센서 범위 설정 (기본값: ±2g)
  this->mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_2);
  
  // 각속도 센서 범위 설정 (기본값: ±250°/s)
  this->mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_250);
  
  // DMP 시작 (Digital Motion Processor)
  this->mpu.dmpInitialize();
  this->mpu.setDMPEnabled(true);
  
  // FIFO(First In First Out) 버퍼 비우기
  this->mpu.resetFIFO();
}

void GyroSensor::getSensorValue() {
  if (mpu.dmpGetCurrentFIFOPacket()) {
    // 가속도(x, y, z) 및 각속도(x, y, z) 값을 읽어옴
    int16_t accelX = mpu.getAccelerationX();
    int16_t accelY = mpu.getAccelerationY();
    int16_t accelZ = mpu.getAccelerationZ();
    int16_t gyroX = mpu.getRotationX();
    int16_t gyroY = mpu.getRotationY();
    int16_t gyroZ = mpu.getRotationZ();

    // 변환된 값을 계산하여 출력
    this->accelX_g = accelX / 16384.0;  // 가속도의 단위: g (1g = 9.8 m/s^2)
    this->accelY_g = accelY / 16384.0;
    this->accelZ_g = accelZ / 16384.0;
    this->gyroX_degPerSec = gyroX / 131.0;  // 각속도의 단위: °/s
    this->gyroY_degPerSec = gyroY / 131.0;
    this->gyroZ_degPerSec = gyroZ / 131.0;
  }
}

float* GyroSensor::getAccel_g() {
  float accel_g[3] = {this->accelX_g, this->accelY_g, this->accelZ_g};
  return accel_g;
}

float* GyroSensor::getGyro_degPerSec() {
  float gyro_degPerSec[3] = {this->gyroX_degPerSec, this->gyroY_degPerSec, this->gyroZ_degPerSec};
  return gyro_degPerSec;
}

float GyroSensor::getAccelX_g() {
  return this->accelX_g;
}

float GyroSensor::getAccelY_g() {
  return this->accelY_g;
}

float GyroSensor::getAccelZ_g() {
  return this->accelZ_g;
}

float GyroSensor::getGyroX_degPerSec() {
  return this->gyroX_degPerSec;
}

float GyroSensor::getGyroY_degPerSec() {
  return this->gyroY_degPerSec;
}

float GyroSensor::getGyroZ_degPerSec() {
  return this->gyroZ_degPerSec;
}