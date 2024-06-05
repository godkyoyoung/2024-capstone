#include "Motor.hpp"


class RobotController {
  private:
    unsigned int currentSpeed = 0;
    
    Motor *motorFL = new Motor(18, 31, 11, 34, 35, true); // Left Front
    Motor *motorFR = new Motor(19, 38, 7, 37, 36, false); // Right Front
    Motor *motorBL = new Motor(3, 49, 6, 43, 42, true);   // Left Back
    Motor *motorBR = new Motor(2, A1, 4, A4, A5, false);  // Right Back

    bool isInterrupted = false;

  public:
    RobotController();
    void forward();
    void backward();
    void right();
    void left();
    void stop();

    void setCurrentSpeed(unsigned int currentSpeed);
    unsigned int getCurrentSpeed();

    long* getEncoderPositions();
    
    void setIsInterrupted(bool isInterrupted);
    bool getIsInterrupted();
};
