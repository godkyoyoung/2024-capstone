# 1. 라이다센서 'YDLidarX2.__exit__(...) is called by: None, None'으로 계속 종료됨
#   -> 안 되면 그냥 라이다센서 안 쓰고 어거지 작동 시켜야 됨
# 2. 모니터링 기능
#  -> 소켓통신을 통해 앱으로 비디오 프레임을 실시간으로 보내려고 했으나 비정상적인 오류로 계속 종료됨 다른 오류코드 없이 'Process finished with exit code 3'만 뜸
#  -> 앱인벤터의 웹뷰어 컴포넌트를 이용하기 위해 웹서버를 만들어야 함
# 3. '전화'라는 문자열이 포함되면 'CALL' 전달, '문자', '메시지'라는 문자열이 포함되면 'msg' 전달. 문자는 문자내용도 지정해주어야 하는뎁
# 4. 전화다이렉트로 걸면 전화 권한이 없다는 오류가 뜸. 전화 권한을 줬는데도.
#   -> Companion으로 테스트하고 계신가요? Google Play Store에서 Companion을 다운로드한 경우 Google은 Companion에 CALL_PHONE 권한을 포함시키지 않습니다.
#    따라서 Play 스토어에서 받은 Companion은 이 권한이 없을 수 있습니다. 권한 포함된 버전을 다운받아야 함 -> 앱으로 다운 받아서 하니까 잘 됨
# 5. 앱에서 로봇on 버튼 누르면 사람 따라가기
# 6. forwardToUser에서 break가 아닌 return으로 루프 종료
#    -> 함수가 호출된 곳으로 돌아가야 할 때 break를 사용하면 함수의 끝으로 이동하여 루프를 종료하게 되지만, return을 사용하면 함수 전체를 종료하고 호출된 곳으로 바로 돌아감
# 7. detectFallen과 locationBodyCenter에서 하나의 카메라 객체를 사용하는 데에서 문제 -> lock 걸어서 한 번에 하나의 스레드만 카메라에 접근할 수 있도록 제어

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')

import cv2
import socket
import threading
import serial
import time

import PoseDetector as pd
from YDLidarX2 import LidarX2
import VoiceChat as vc

serial = serial.Serial('COM3', 115200)
class FallenDetectRobot:
    def __init__(self):
        self.detector = pd.poseDetector()
        self.threshold = 35  # 쓰러짐 판단 임계값 35도
        self.fallen_detected = False # 쓰러짐 감지 플래그
        self.fallen_start_time = None  # 쓰러짐 시작 시간
        self.fallen_duration_threshold = 5  # 쓰러짐 상태를 유지해야 하는 시간(초)
        self.robot_state = None # 로봇 현재 동작 상태
        self.target_distance = 2000  # 목표 거리
        self.move_ready = False  # 몸 중앙이 화면 중앙에 위치하는가
        self.lock = threading.Lock()  # 쓰레드 간 동기화를 위한 락 객체
        self.voicechat = vc.VoiceChat('stt_key.json', 'tts_key.json', "")
        self.cap = None  # 카메라 캡처 객체
        self.current_frame = None  # 현재 프레임 공유 변수
        self.input_cnt = 0

    # 쓰러짐 탐지
    def detectFallen(self, conn):
        while True:
            with self.lock:
                success, img = self.cap.read()
                if not success:
                    break

                img = self.detector.findPose(img, False)
                lmlist = self.detector.getPosition(img, False)

                if len(lmlist) != 0:
                    # 왼쪽 어깨(11), 왼쪽 골반(23)
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

                    # self.robotControl()  # 로봇 작동 시작
                    # if self.robot_state == 'S':  # 로봇이 사용자에게 도달하면 대화
                    #     self.handleClient()
                    #     # 사용자의 응답이 전혀 없는 경우는 바로 119에 신고
                    #     if self.input_cnt == 0:
                    #         call_119 = "사용자의 응답이 없습니다. 의식이 없는 상태로 판단하여 119를 부르겠습니다."
                    #         print(call_119)
                    #         self.voicechat.audioPlay(self.voicechat.textToSpeech(call_119))
                    #         conn.send("119".encode('utf-8'))
                    #         break
                    #     if "전화" in self.voicechat.messages.index(-1):
                    #         conn.send("call".encode('utf-8'))
                    #         print("call 전송")
                    #         # conn.send(self.voicechat.messages.index(-1).encode('utf-8'))
                    #         # print("마지막 대화 전송")

                    self.handleClient()

                    # 사용자의 응답이 전혀 없는 경우는 바로 119에 신고
                    if self.input_cnt == 0:
                        call_119 = "사용자의 응답이 없습니다. 의식이 없는 상태로 판단하여 119를 부르겠습니다."
                        print(call_119)
                        self.voicechat.audioPlay(self.voicechat.textToSpeech(call_119))
                        conn.send("119".encode('utf-8'))
                        break
                    else:
                        if "전화" or "연결" in self.voicechat.messages[3].keys(): # 전화 명령이라면
                            conn.send("call".encode('utf-8'))
                            print("call 전송")
                            break
                            # conn.send(self.voicechat.messages.index(-1).encode('utf-8'))
                            # print("마지막 대화 전송")
                        elif "문자" or "메시지" or "메세지" in self.voicechat.messages[2].keys(): # 문자 명령이라면
                            conn.send("msg".encode('utf-8'))
                            print("msg 전송")
                            break

                cv2.imshow("image", img)
                cv2.waitKey(1)

    # 로봇 제어
    def robotControl(self):
        camera_thread = threading.Thread(target=self.locationBodyCenter)
        lidar_thread = threading.Thread(target=self.forwardToUser)
        camera_thread.start()
        lidar_thread.start()
        camera_thread.join()
        lidar_thread.join()

        self.fallen_detected = False  # 쓰러짐 탐지 후 플래그 초기화

    def locationBodyCenter(self):
        while True:
            with self.lock:
                success, img = self.cap.read()  # 카메라에서 새로운 프레임을 읽어옴
                if not success:
                    break

                if img is None:
                    continue

                img = self.detector.findPose(img, False)
                lmlist = self.detector.getPosition(img, False)

                h, w, c = img.shape

                # 몸 중앙이 들어와야 하는 화면 가로 범위
                start_x = w * 10 // 21
                end_x = w * 11 // 21

                center_x, center_y = None, None
                if len(lmlist) != 0:
                    center_x, center_y = self.detector.getBodycenter(img)

                if center_x is not None:
                    if center_x < start_x:
                        with self.lock:
                            self.move_ready = False
                        serial.write('R'.encode('utf-8'))
                        print('R')
                    elif center_x > end_x:
                        with self.lock:
                            self.move_ready = False
                        serial.write('L'.encode('utf-8'))
                        print('L')
                    else:
                        with self.lock:
                            self.move_ready = True
                            print("사용자 화면 중앙 위치 완료")
                            break

                cv2.imshow("image", img)
                cv2.waitKey(1)

    def forwardToUser(self):
        with LidarX2() as lidar:
            while True:
                with self.lock:
                    if self.move_ready:
                        result = lidar.getPolarResults()
                        filtered_result = {key: value for key, value in result.items()
                                           if int(key) in range(0, 20) or int(key) in range(340, 360)}
                        print(filtered_result)
                        filtered_values = [value for value in filtered_result.values() if value != 0]  # 0이 아닌 값만 필터링

                        if filtered_values:  # 리스트가 비어있지 않다면
                            min_value = min(filtered_values)  # 최소값 계산
                            print(min_value)
                            if min_value >= self.target_distance:
                                serial.write('F'.encode('utf-8'))
                                print('F')
                            elif min_value < self.target_distance:
                                serial.write('S'.encode('utf-8'))
                                print('S')
                                break
                        else:
                            print("리스트 비어있음")
                            break

    def handleClient(self):
        gpt_response_voice = self.voicechat.textToSpeech(self.voicechat.init_question)
        self.voicechat.audioPlay(gpt_response_voice)
        while True:
            user_input_voice = self.voicechat.audioRecord()
            user_input_text = self.voicechat.speechToText(user_input_voice)
            if not user_input_text.strip():  # 변환된 텍스트가 비어 있는지 확인
                print("사용자의 입력이 없습니다. 대화를 종료합니다.")
                break  # 사용자가 더 이상 말하지 않으면 루프 종료

            gpt_response = self.voicechat.getGptResponse(user_input_text)
            print(gpt_response)
            gpt_response_voice = self.voicechat.textToSpeech(gpt_response)
            self.voicechat.audioPlay(gpt_response_voice)
            self.input_cnt += 1



def main():
    fallendetectrobotinstance = FallenDetectRobot()
    video_path = '../CapstoneProject0602/CapstoneProject/testData/fallen04-1.mp4'
    fallendetectrobotinstance.cap = cv2.VideoCapture(0)

    server_socket = socket.socket()
    server_socket.bind(('192.168.0.112', 12345))
    server_socket.listen(5)
    print("서버가 시작되었습니다. 클라이언트 연결을 기다리는 중...")

    conn, addr = server_socket.accept()
    print(f"클라이언트가 연결되었습니다: {addr}")
    detection_thread = threading.Thread(target=fallendetectrobotinstance.detectFallen, args=(conn,))
    detection_thread.start()
    # following_thread = threading.Thread(target=fallendetectrobotinstance.robotUserFollowing, args=(conn,))
    # following_thread.start()

    detection_thread.join()
    # following_thread.join()

    # main 함수가 종료될 때 카메라 캡처 객체와 소켓 연결을 해제
    fallendetectrobotinstance.cap.release()
    conn.close()

if __name__ == "__main__":
    main()


    # # 로봇 사용자 팔로잉
    # def robotUserFollowing(self, conn):
    #     while True:
    #         data = conn.recv(1024).decode()
    #         if data:
    #             camera_thread = threading.Thread(target=self.locationBodyCenter)
    #             camera_thread.start()
    #             with LidarX2() as lidar:
    #                 while True:
    #                     with self.lock:
    #                         if self.move_ready:
    #                             result = lidar.getPolarResults()
    #                             filtered_result = {key: value for key, value in result.items()
    #                                                if int(key) in range(0, 20) or int(key) in range(340, 360)}
    #                             filtered_values = list(filtered_result.values())
    #
    #                             for value in filtered_values:
    #                                 if value > self.target_distance:
    #                                     serial.write('F'.encode('utf-8'))
    #                                     print('F')
    #                                 else:
    #                                     serial.write('B'.encode('utf-8'))
    #                                     print('B')



    # # 앱으로 실시간 비디오 프레임 전송
    # def sendFrame(self, conn):
    #     try:
    #         while True:
    #             with self.lock:
    #                 frame = self.current_frame
    #             if frame is None:
    #                 continue
    #
    #             # 여기서부터 프레임 처리 및 전송 작업을 수행합니다.
    #             # 프레임을 바이트로 인코딩
    #             frame_data = pickle.dumps(frame)
    #             # 바이트 데이터의 길이를 패킹
    #             message_size = struct.pack("L", len(frame_data))
    #             # 이미지 데이터 전송
    #             conn.sendall(message_size + frame_data)
    #     except Exception as e:
    #         print("Exception in sendFrame:", e)
    #     finally:
    #         # main 함수가 종료될 때 카메라 캡처 객체와 소켓 연결을 해제
    #         self.cap.release()
    #         conn.close()