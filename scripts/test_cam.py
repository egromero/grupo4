import sys
import cv2
import numpy as np

video_capture = cv2.VideoCapture(0)

while True:
    ret, frame_bgr = video_capture.read()
    frame_lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
    reduced_frame = cv2.resize(frame_lab, (320,240))
    retth, MASK = cv2.threshold(reduced_frame[:,:,1], 150, 255, cv2.THRESH_BINARY)

    cv2.imshow('Mascara rojos', np.concatenate((reduced_frame[:,:,1], MASK), axis=1))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
