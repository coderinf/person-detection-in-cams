import cv2
from cvzone.PoseModule import PoseDetector
import pyglet.media
import threading
import os
import requests

cap = cv2.VideoCapture(0) #webcampip


if not cap.isOpened():
    print("Camera can't open!!!")
    exit()

detector = PoseDetector()
sound = pyglet.media.load("red-alert_nuclear_buzzer-99741.mp3", streaming=False)
people = False
img_count, breakcount = 0, 0



def sendTelegram():
    path = "C:\\Users\\coder\\PycharmProjects\\PROJECT EXPO"  # Replace your path directory
    url = 'https://api.telegram.org/bot'
    token = "5925692200:AAGiOqrvaAKAZOx0SW__Ypst6--kG62zUes"  # Replace Your Token Bot
    chat_id = '-1001837443634'  # Replace Your Chat ID
    caption = "People Detected!!! "
    cv2.imwrite(os.path.join(path, img_name), img)
    import telepot
    bot = telepot.Bot('5925692200:AAGiOqrvaAKAZOx0SW__Ypst6--kG62zUes')

    # here replace chat_id and test.jpg with real things
    bot.sendPhoto('-1001837443634', photo=open(img_name, 'rb'))
    files = {'photo': open(path + img_name, 'rb')}
    """resp = requests.post(url + token + '/sendPhoto?chat_id=' + chat_id + '&caption=' + caption, files=files)
    print(f'Response Code: {resp.status_code}')"""


while True:
    success, img = cap.read()
    img = detector.findPose(img, draw=False)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False)
    img_name = f'image_{img_count}.png'

    teleThread = threading.Thread(target=sendTelegram, args=())
    soundThread = threading.Thread(target=sound.play, args=())

    if bboxInfo:
        cv2.rectangle(img, (120, 20), (470, 80), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, "PEOPLE DETECTED!!!", (130, 60),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        breakcount += 1

        if breakcount >= 30:
            if people == False:
                img_count += 1
                soundThread.start()
                teleThread.start()
                people = not people
    else:
        breakcount = 0
        if people:
            people = not people

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('0'):
         break

cv2.destroyAllWindows()
