#include "RobotController.hpp"
#include <SoftwareSerial.h>

RobotController robotController;

#define BTN_PIN 10

void setup()
{
  pinMode(BTN_PIN, INPUT);
  Serial.begin(115200);
  robotController = RobotController();
}
 
void loop()
{
  // int interrupt = digitalRead(BTN_PIN);
  // if(interrupt == HIGH){
  //   robotController.setIsInterrupted(
  //     !robotController.getIsInterrupted()
  //   );
  // }
  if(0){
    robotController.stop();
  } else {
    readOperation(robotController);
  }
}

void readOperation(RobotController robotController){
  int readLen = Serial.available();
  if(readLen){
    for(int i = 0; i < readLen; i++){
      char operation = Serial.read();
      int power = 20;    // Serial.parseInt();
      Serial.println(operation);
      // Serial.println(power);
      if (power != 0) {
        robotController.setCurrentSpeed(power);
      }
      switch(operation){
        case 'F':
          robotController.forward();
          break;
        case 'B':
          robotController.backward();
          break;
        case 'R':
          robotController.right();
          break;
        case 'L':
          robotController.left();
          break;
        case 'S':
          robotController.stop();
          break;
      }
    }
  }
}

