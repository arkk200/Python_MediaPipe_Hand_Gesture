import cv2
import mediapipe as mp
import math
import time

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import screen_brightness_control as sbc

FRAME_DELAY = 1

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

cap = cv2.VideoCapture(0)

mpHands = mp.solutions.hands
my_hands = mpHands.Hands(max_num_hands=10)
mpDraw = mp.solutions.drawing_utils

def dist(x1,y1,x2,y2):
    return math.sqrt(math.pow(x1-x2,2))+math.sqrt(math.pow(y1-y2,2))

volume_size = -65
current_brightness = 100

compareIndex = [[18,4],[6,8],[10,12],[14,16],[18,20]]
open =[False,False,False,False,False]
gesture = [
    [True, True, False, False, False, "Volume Up"], # 엄지, 검지
    [False, True, False, False, True, "Volume Down"], # 소지, 검지
    [True, False, False, False, False, "Brightness Up"], # 엄지
    [False, False, False, False, True, "Brightness Down"], # 소지
    [False, False, True, False, False, "Fxck you"], # 중지
    [True, False, True, False, True, "Ultra Fxck you"], # 엄지, 중지, 소지
    [True, False, True, False, False, "Original Fxck you"] # 엄지, 중지
]

while True:
    success,img=cap.read()
    h,w,c=img.shape
    img = cv2.flip(img, 1)
    imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    results=my_hands.process(imgRGB)
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for i in range(0,5):
                open[i]=dist(handLms.landmark[0].x,handLms.landmark[0].y,handLms.landmark[compareIndex[i][0]].x,handLms.landmark[compareIndex[i][0]].y) < dist(handLms.landmark[0].x,handLms.landmark[0].y,handLms.landmark[compareIndex[i][1]].x,handLms.landmark[compareIndex[i][1]].y)
            
            # print(open)
            text_x=(handLms.landmark[0].x*w)
            text_y=(handLms.landmark[0].y*h)
            for i in range(0,len(gesture)):
                flag=True
                for j in range(5):
                    if(gesture[i][j]!=open[j]):
                        flag=False
                if(flag==True):
                    if i == 0:
                        volume_size += 0.5
                        volume_size = min(volume_size, 0)
                        volume.SetMasterVolumeLevel(volume_size, None)
                    elif i == 1:
                        volume_size -= 0.5
                        volume_size = max(volume_size, -65)
                        volume.SetMasterVolumeLevel(volume_size, None)
                    elif i == 2:
                        current_brightness += 2
                        current_brightness = min(current_brightness, 100)
                        sbc.set_brightness(current_brightness)
                        pass
                    elif i == 3:
                        current_brightness -= 2
                        current_brightness = max(current_brightness, 0)
                        sbc.set_brightness(current_brightness)
                        pass
                    cv2.putText(
                        img,
                        gesture[i][5],(round(text_x)-50,round(text_y)-100), 
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,(51,255,51),4)
                    
            mpDraw.draw_landmarks(img,handLms,mpHands.HAND_CONNECTIONS)
    
    cv2.imshow("HandTracking", img)
    cv2.waitKey(FRAME_DELAY)