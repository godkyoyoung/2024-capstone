#ifndef ARDUINO
#include <Arduino.h>
#define ARDUINO
#endif

#include "RobotController.hpp"
#include "RobotControllerConstant.hpp"

#ifndef PINMAP

#define PWMA 4
#define DIRA1 A4
#define DIRA2 A5

#define PWMB 6
#define DIRB1 43
#define DIRB2 42

#define PWMC 11
#define DIRC1 34
#define DIRC2 35

#define PWMD 7
#define DIRD1 37
#define DIRD2 36

#define FORWARD 1
#define BACKWARD 0

#define PINMAP
#endif


RobotController::RobotController() {
    // pinMode(PWMA, OUTPUT);
    // pinMode(PWMB, OUTPUT);
    // pinMode(PWMC, OUTPUT);
    // pinMode(PWMD, OUTPUT);

    // pinMode(DIRA1, OUTPUT);
    // pinMode(DIRA2, OUTPUT);
    // pinMode(DIRB1, OUTPUT);
    // pinMode(DIRB2, OUTPUT);
    // pinMode(DIRC1, OUTPUT);
    // pinMode(DIRC2, OUTPUT);
    // pinMode(DIRD1, OUTPUT);
    // pinMode(DIRD2, OUTPUT);
}

void RobotController::forward() {
  this->motorFL->setSpeed(this->currentSpeed);
  this->motorFR->setSpeed(this->currentSpeed);
  this->motorBL->setSpeed(this->currentSpeed);
  this->motorBR->setSpeed(this->currentSpeed);
}

void RobotController::backward() {
  this->motorFL->setSpeed(-this->currentSpeed);
  this->motorFR->setSpeed(-this->currentSpeed);
  this->motorBL->setSpeed(-this->currentSpeed);
  this->motorBR->setSpeed(-this->currentSpeed);
}

void RobotController::right() {
  this->motorFL->setSpeed(this->currentSpeed);
  this->motorFR->setSpeed(-this->currentSpeed);
  this->motorBL->setSpeed(-this->currentSpeed);
  this->motorBR->setSpeed(this->currentSpeed);
}

void RobotController::left() {
  this->motorFL->setSpeed(-this->currentSpeed);
  this->motorFR->setSpeed(this->currentSpeed);
  this->motorBL->setSpeed(this->currentSpeed);
  this->motorBR->setSpeed(-this->currentSpeed);
}

void RobotController::stop() {
  this->motorFL->hardStop();
  this->motorFR->hardStop();
  this->motorBL->hardStop();
  this->motorBR->hardStop();
}

void RobotController::setCurrentSpeed(unsigned int currentSpeed) {
    this->currentSpeed = currentSpeed;
}

unsigned int RobotController::getCurrentSpeed() {
    return this->currentSpeed;
}

long* RobotController::getEncoderPositions() {
    long* encoderPositions = new long[4];
    encoderPositions[0] = this->motorFL->getEncoderPosition();
    encoderPositions[1] = this->motorFR->getEncoderPosition();
    encoderPositions[2] = this->motorBL->getEncoderPosition();
    encoderPositions[3] = this->motorBR->getEncoderPosition();
    return encoderPositions;
}

void RobotController::setIsInterrupted(bool isInterrupted) {
    this->isInterrupted = isInterrupted;
}

bool RobotController::getIsInterrupted() {
    return this->isInterrupted;
}