# 3. 카메라 영상이 5초 가량 잘 작동하다가 멈춤

import PoseDetector as pd
from YDLidarX2 import LidarX2
import cv2
import serial

detector = pd.poseDetector()
serial = serial.Serial('COM3', 115200)

video_path = './testData/fallen04.mp4'
cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    if not success:
        break

    img = detector.findPose(img, False)
    lmList = detector.getPosition(img, False)
    h, w, c = img.shape
    center_x, center_y = detector.getBodycenter(img)

    if center_x < w / 2:
        # center_x == w/2까지 로봇 오른쪽으로
        serial.write('R')
        print('R'.encode('utf-8'))
    elif center_x > w / 2:
        # center_x == w/2까지 로봇 왼쪽으로
        serial.write('L'.encode('utf-8'))
        print('L')

    if center_x == w / 2:
        Lidar = LidarX2()  # 객체 만들고
        with Lidar as lidar:  # with문으로 열어서 사용 => 자동으로 스캔 시작.
            # with문을 벗어나면 자동으로 Serial 연결 끊어지고, Thread 종료함
            while True:
                result = lidar.getPolarResults()  # 극좌표계 결과 받아오기
                for key, value in result.items():
                    angle = int(key)
                    if angle == 0:
                        print(f"Angle: {angle}, Distance: {value}")
                        if value > 1500:
                            serial.write('F'.encode('utf-8'))
                            print('F')
                        else:
                            serial.write('S'.encode('utf-8'))
                            print('S')

    cv2.imshow("image", img)
    cv2.waitKey(1)