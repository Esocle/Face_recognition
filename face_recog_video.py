# face_recog.py

import face_recognition
import cv2
import os
import numpy as np

class FaceRecog():
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        # self.camera = camera.VideoCamera()

        self.known_face_encodings = []
        self.known_face_names = []

        # Load sample pictures and learn how to recognize it.
        dirname = 'knowns'
        files = os.listdir(dirname)
        for filename in files:
            name, ext = os.path.splitext(filename)
            if ext == '.jpg':
                self.known_face_names.append(name)
                pathname = os.path.join(dirname, filename)
                img = face_recognition.load_image_file(pathname)
                face_encoding = face_recognition.face_encodings(img)[0]
                self.known_face_encodings.append(face_encoding)

        # Initialize some variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.process_this_frame = True

    # def __del__(self):
    #     del self.camera

    def get_frame(self, path):
        # Grab a single frame of video
        vidcap = cv2.VideoCapture(path)
        cnt = 1
        wrong = 0
        while True:
            ret, frame = vidcap.read()
            if ret == False:
                break
            if(int(vidcap.get(1)) % 30 != 0):
                continue
            # frame = cv2.imread(image)

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if self.process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    min_value = min(distances)

                    # tolerance: How much distance between faces to consider it a match. Lower is more strict.
                    # 0.6 is typical best performance.
                    name = "Unknown"
                    if min_value < 0.6:
                        index = np.argmin(distances)
                        name = self.known_face_names[index]

                    self.face_names.append(name)

            self.process_this_frame = not self.process_this_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
                cv2.imwrite("detect/V/test%d.jpg" % cnt, frame)
                print('Saved frame%d.jpg' % cnt)        # 이미지 저장
                cnt += 1
                if name != 'V':           # 이름판별
                    wrong += 1
            
        return ((cnt-wrong) / cnt * 100)
    

if __name__ == '__main__':
    face_recog = FaceRecog()
    results = face_recog.get_frame('video/V.mp4')
    print(f'{results}%')        # 정확도
