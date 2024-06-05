
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')

import PoseDetector as pd
from YDLidarX2 import LidarX2
import cv2
import serial
import threading

detector = pd.poseDetector()
serial = serial.Serial('COM3', 115200)
target_distance = 2500   # 목표 거리
move_ready = False
lock = threading.Lock()  # 쓰레드 간 동기화를 위한 락 객체

cap = cv2.VideoCapture(0)
def locationBodyCenter():
    global move_ready
    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findPose(img, False)
        lmList = detector.getPosition(img, False)
        h, w, c = img.shape
        #몸 중앙이 들어와야 하는 화면 가로 범위
        start_x = w * 10 // 21
        end_x = w * 11 // 21

        center_x, center_y = None, None
        if len(lmList) != 0:
            center_x, center_y = detector.getBodycenter(img)

        if center_x is not None:
            if center_x < start_x:
                serial.write('R'.encode('utf-8'))
                print('R')
            elif center_x > end_x:
                serial.write('L'.encode('utf-8'))
                print('L')
            else:
                with lock:
                    move_ready = True
                    print("사용자 화면 중앙 위치 완료")

        cv2.imshow("image", img)
        if cv2.waitKey(1) == ord('q'):
            break

def forwardToUser():
    global move_ready
    with LidarX2() as lidar:
        while True:
            with lock:
                if move_ready:
                    result = lidar.getPolarResults()
                    filtered_result = {key:value for key, value in result.items()
                                       if int(key) in range(0, 20) or int(key) in range(340, 360)}
                    print(filtered_result)
                    filtered_values = list(filtered_result.values())

                    for value in filtered_values:
                        if value != 0:
                            print(value)
                            if value >= target_distance:
                                serial.write('F'.encode('utf-8'))
                                print('F')
                            else:
                                serial.write('B'.encode('utf-8'))
                                print('B')
                            break # 사람과 로봇 사이의 거리를 한 번만 체크하고 종료

# 각각의 작업을 병렬로 실행
camera_thread = threading.Thread(target=locationBodyCenter)
lidar_thread = threading.Thread(target=forwardToUser)
camera_thread.start()
lidar_thread.start()

camera_thread.join()
lidar_thread.join()

cap.release()
cv2.destroyAllWindows()

# while True:
#     success, img = cap.read()
#     if not success:
#         break
#
#     img = detector.findPose(img, False)
#     lmList = detector.getPosition(img, False)
#     h, w, c = img.shape
#     # 몸 중앙이 들어와야 하는 화면 가로 범위
#     # start_x = w * 4 // 9
#     # end_x = w * 5 // 9
#
#     if len(lmList) != 0:
#         center_x, center_y = detector.getBodycenter(img)
#
#     if center_x < w//2:
#         # center_x == w/2까지 로봇 오른쪽으로
#         serial.write('R'.encode('utf-8'))
#         print('R')
#
#     elif center_x > w//2:
#         # center_x == w/2까지 로봇 왼쪽으로
#         serial.write('L'.encode('utf-8'))
#         print('L')
#
#     else:
#         if not is_forward:
#             is_forward = True  # 전진 상태로 전환
#             Lidar = LidarX2()  # 객체 만들고
#             with Lidar as lidar:  # with문으로 열어서 사용 => 자동으로 스캔 시작.
#                 # with문을 벗어나면 자동으로 Serial 연결 끊어지고, Thread 종료함
#                 while True:
#                     result = lidar.getPolarResults()  # 극좌표계 결과 받아오기
#                     for key, value in result.items():
#                         angle = int(key)
#                         if angle == 12:
#                             print(f"Angle: {angle}, Distance: {value}")
#                             if value > target_distance:
#                                 serial.write('F'.encode('utf-8'))
#                                 print('F')
#                             else:
#                                 serial.write('S'.encode('utf-8'))
#                                 print('S')
#                                 is_forward = False  # 전진 상태 해제
#
#
#
#     cv2.imshow("image", img)
#     if cv2.waitKey(1) == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()