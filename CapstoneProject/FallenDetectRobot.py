# 음성 데이터를 보내기 위해서는 데이터의 길이를 먼저 전송하고, 그 다음에 실제 데이터를 전송해야함
# 문제 : 앱인벤터에서 음성파일을 받는 방법을 모르겠음

import cv2
import socket
import threading
import serial
import os
import time

import PoseDetector as pd
from YDLidarX2 import LidarX2
import VoiceChat as vc

# serial = serial.Serial('COM3', 115200)
class FallenDetectRobot:
    def __init__(self):
        self.detector = pd.poseDetector()
        self.threshold = 35  # 쓰러짐 판단 임계값 35도
        self.fallen_detected = False # 쓰러짐 감지 플래그
        self.fallen_start_time = None  # 쓰러짐 시작 시간
        self.fallen_duration_threshold = 3  # 쓰러짐 상태를 유지해야 하는 시간 (초)
        self.voicechat = vc.VoiceChat('stt_key.json', 'tts_key.json', os.getenv("OPENAI_API_KEY"))
    
    # 쓰러짐 탐지
    def detectFallen(self, cap, conn):
        while True:
            success, img = cap.read()
            if not success:
                break
            
            img = self.detector.findPose(img)

            lmList = self.detector.getPosition(img, False)
            if len(lmList) != 0:
                # 왼쪽 어깨(11), 왼쪽 골반(23)
                # 오른쪽 관절들로 판단 -> 왼쪽 관절들로 변경 더 잘 됨 왜지
                angle = self.detector.getAngle(img, 11, 23)
                cv2.putText(img, str(angle), (200, 200), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255))
                # 지면과 상체와 사이 각도가 임계값 미만이면 쓰러짐으로 판단
                if angle < self.threshold:
                    if not self.fallen_detected:
                        self.fallen_start_time = time.time()  # 첫 탐지 시간
                    self.fallen_detected = True
                else:
                    self.fallen_detected = False
                    self.fallen_start_time = None

            # 쓰러짐이 일정 시간(10초)동안 유지되었는지 확인
            if self.fallen_detected and time.time() - self.fallen_start_time >= self.fallen_duration_threshold:
                cv2.putText(img, "Fallen", (500, 500), cv2.FONT_HERSHEY_TRIPLEX, 5, (0, 0, 255))
                conn.send("fallen".encode('utf-8'))  # 쓰러짐 발생시 앱으로 보고
                self.handleClient(conn)  # handleClient 메서드 호출
                # break  # 쓰러짐이 감지되면 더 이상 프레임을 처리하지 않음

            cv2.imshow("image", img)
            cv2.waitKey(1)


    # 로봇 제어
    def robotControl(self, cap):
        while True:
            if self.fallen_detected:  # 쓰러짐이 감지되면 실행
                success, img = cap.read()
                if not success:
                    break

                img = self.detector.findPose(img, False)
                lmList = self.detector.getPosition(img, False)

                h, w, c = img.shape
                center_x, center_y = self.detector.getBodycenter(img)

                if center_x < w / 2:
                    # center_x == w/2까지 로봇 오른쪽으로
                    serial.write('R'.encode('utf-8'))
                    print('R')
                elif center_x > w / 2:
                    # center_x == w/2까지 로봇 왼쪽으로
                    serial.write('L'.encode('utf-8'))
                    print('L')

                if center_x == w/2:
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
                self.fallen_detected = False  # 쓰러짐 탐지 후 플래그 초기화


    def handleClient(self, conn):
        try:
            # 서버에서 대화 시작
            initVoice = "initVoice.mp3"
            audio_length = len(initVoice)
            conn.sendall(audio_length.to_bytes(4, byteorder='big'))
            conn.sendall(initVoice.encode())

            # 클라이언트로부터 데이터 수신
            while True:
                data = conn.recv(1024)
                if not data:
                    break

                # 받아온 음성 데이터 텍스트로 변환
                file_name = data
                stt_result = self.voicechat.speechToText(file_name)

                # 응답 생성
                gpt_response = self.voicechat.getGptResponse(stt_result)

                # gpt 응답 음성 파일로 변환
                tts_result = self.voicechat.textToSpeech(gpt_response)

                # 음성 파일을 앱으로 전송
                audio_length = len(tts_result)
                conn.sendall(audio_length.to_bytes(4, byteorder='big'))
                conn.sendall(tts_result.encode())

        except ConnectionResetError:
            print("ConnectionResetError: 클라이언트와의 연결이 강제로 종료되었습니다.")
        except ConnectionAbortedError:
            print("ConnectionAbortedError: 클라이언트와의 연결이 중단되었습니다.")
        finally:
            conn.close()


def main():
    fallendetectrobotinstance = FallenDetectRobot()
    video_path = './testData/fallen04.mp4'
    cap = cv2.VideoCapture(video_path)

    server_socket = socket.socket()
    server_socket.bind(('210.99.115.16', 12345))
    server_socket.listen(5)

    while True:
        conn, addr = server_socket.accept()
        detection_thread = threading.Thread(target=fallendetectrobotinstance.detectFallen, args=(cap, conn))
        detection_thread.start()
        # control_thread = threading.Thread(target=fallendetectrobotinstance.robotControl, args=(cap,))
        # control_thread.start()


if __name__ == "__main__":
    main()
