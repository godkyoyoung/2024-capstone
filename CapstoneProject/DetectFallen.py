
import cv2
import PoseDetector as pd
import socket
import threading

class DetectFallen:
    def __init__(self):
        self.detector = pd.poseDetector()
        self.threshold = 35  # 쓰러짐 판단 임계값 35도

    def detectFallen(self, cap, conn):
        while True:
            success, img = cap.read()
            if not success:
                break

            img = self.detector.findPose(img)

            lmList = self.detector.getPosition(img, False)
            if len(lmList) != 0:
                # 머리(0), 오른쪽 어깨(12), 오른쪽 골반(24), 왼쪽 어깨(11), 왼쪽 골반(23)
                # 오른쪽 관절들로 판단 -> 왼쪽 관절들로 변경 더 잘 됨 왜지
                angle = self.detector.getAngle(img, 11, 23)
                cv2.putText(img, str(angle), (200, 200), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255))
                # 지면과 상체와 사이 각도가 임계값 미만이면 쓰러짐으로 판단
                if angle < self.threshold:
                    cv2.putText(img, "Fallen", (500, 500), cv2.FONT_HERSHEY_TRIPLEX, 5, (0, 0, 255))
                    conn.send("fallen".encode('utf-8'))  # 쓰러짐 발생시 앱으로 보고

            cv2.imshow("image", img)
            cv2.waitKey(1)

        conn.close()

def main():
    detectfalleninstance = DetectFallen()
    video_path = 'testData/fallen04.mp4'
    cap = cv2.VideoCapture(video_path)

    server_socket = socket.socket()
    server_socket.bind(('', 12345))
    server_socket.listen(5)

    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=detectfalleninstance.detectFallen, args=(cap, conn))
        client_thread.start()

if __name__ == "__main__":
    main()
