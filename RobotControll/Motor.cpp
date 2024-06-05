#include "Motor.hpp"

#ifndef LOW
#define LOW 0
#endif
#ifndef HIGH
#define HIGH 1
#endif

Motor::Motor(int encoderA, int encoderB, int pinPWM, int dir1, int dir2, bool encoderReversed) {
  this->_encoder = new Encoder(encoderA, encoderB);
  this->_motorPWM = pinPWM;
  this->_motorDir1 = dir1;
  this->_motorDir2 = dir2;
  this->encoderReversed = encoderReversed;
  pinMode(this->_motorPWM, OUTPUT);
  pinMode(this->_motorDir1, OUTPUT);
  pinMode(this->_motorDir2, OUTPUT);
}

void Motor::setSpeed(int speed) {
  if(speed != 0) {
    this->_speed = speed;
  }
  if(this->_speed > 0) {
    digitalWrite(this->_motorDir1, HIGH);
    digitalWrite(this->_motorDir2, LOW);
    analogWrite(this->_motorPWM, this->_speed < 255 ? this->_speed : 255);
  } else if(this->_speed < 0) {
    digitalWrite(this->_motorDir1, LOW);
    digitalWrite(this->_motorDir2, HIGH);
    analogWrite(this->_motorPWM, this->_speed > -255 ? -this->_speed : 255);
  }
}

void Motor::hardStop() {
  this->_speed = 0;
  digitalWrite(this->_motorDir1, HIGH);
  digitalWrite(this->_motorDir2, HIGH);
  analogWrite(this->_motorPWM, 0);
}

int Motor::getSpeed() {
  return this->_speed;
}

long Motor::getEncoderPosition() {
  long position = this->_encoder->read();
  return this->encoderReversed ? -position : position;
}