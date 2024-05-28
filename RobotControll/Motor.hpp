#include <Encoder.h>

class Motor {
private:
  Encoder *_encoder;
  bool encoderReversed;
  int _motorPWM, _motorDir1, _motorDir2;
  int _speed;
public:
  Motor(int encoderA, int encoderB, int pinPWM, int dir1, int dir2, bool encoderReversed);
  void setSpeed(int speed);
  int getSpeed();

  void hardStop();

  long getEncoderPosition();
};