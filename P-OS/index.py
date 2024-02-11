# my line token
# wKmy2APAY7sfT9Vrnqx3aI7garZkz51FMwHItR8wdll

import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime
import pytz

import subprocess

import cv2

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
gun_cascade = cv2.CascadeClassifier('classifier/cascade.xml')

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
pinpir = 17
pinredled = 18
pinblueled = 24

pinunlockGreenLED = 27
pinlockRedLED = 25

pinunlockBtn = 5
pinlockBtn = 6

print("PIR Module Test (CTRL-C to exit)")

url = 'https://notify-api.line.me/api/notify'
token = 'wKmy2APAY7sfT9Vrnqx3aI7garZkz51FMwHItR8wdll'
headers = {'Authorization': 'Bearer ' + token}

image_path = '/home/os/Motion_Capture.jpg'
image_file = {'imageFile': (image_path, open(image_path, 'rb'), 'image/jpeg')}

# Set pins as input/output
GPIO.setup(pinpir, GPIO.IN)
GPIO.setup(pinredled, GPIO.OUT)
GPIO.setup(pinblueled, GPIO.OUT)
GPIO.setup(pinunlockGreenLED, GPIO.OUT)
GPIO.setup(pinlockRedLED, GPIO.OUT)

GPIO.setup(pinunlockBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(pinlockBtn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variables to hold the current and last states
currentstate = 0
previousstate = 0

is_locked = False
is_lockedold = False
gun_exit = False
peoPle_exit = False
msg1 = ""
msg2 = ""
try:
    print("Waiting for PIR to settle ...")
    
    while GPIO.input(pinpir) == 1:
        currentstate = 0
    print(" Ready")
    
    while True:
         # Check lock button
        if GPIO.input(pinlockBtn) == GPIO.LOW:
            is_locked = True
            is_lockedold = True
            print("System Locked")
            GPIO.output(pinunlockGreenLED, GPIO.LOW)
            GPIO.output(pinlockRedLED, GPIO.HIGH)
            time.sleep(0.2)
        
        # Check unlock button
        elif GPIO.input(pinunlockBtn) == GPIO.LOW:
            is_locked = False
            is_lockedold = False
            print("System Unlocked")
            GPIO.output(pinunlockGreenLED, GPIO.HIGH)
            GPIO.output(pinlockRedLED, GPIO.LOW)
            time.sleep(0.2)
            
        #elif (is_locked != is_lockedold) :
        #    is_lockedold = flas
        #    print("System Unlocked")
        #    GPIO.output(pinunlockGreenLED, GPIO.HIGH)
        #    GPIO.output(pinlockRedLED, GPIO.LOW)
        #    time.sleep(0.2)
            
        currentstate = GPIO.input(pinpir)
        if currentstate == 1 and previousstate == 0:
            print(" Motion detected!")
             
            for x in range(0, 3):
                GPIO.output(pinredled, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(pinredled, GPIO.LOW)
                GPIO.output(pinblueled, GPIO.HIGH)
                time.sleep(0.2)
                GPIO.output(pinblueled, GPIO.LOW)
                time.sleep(0.2)
            
            image_filename = "Motion_Capture.jpg"
            subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", image_filename])
            image_path = '/home/os/Motion_Capture.jpg'
            image_file = {'imageFile': (image_path, open(image_path, 'rb'), 'image/jpeg')}
            img = cv2.imread(image_filename) 
            # Convert into grayscale 
            grayFace = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            grayGun = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Detect 
            faces = face_cascade.detectMultiScale(grayFace, 1.1, 4)
            guns = gun_cascade.detectMultiScale(grayGun, 1.3, 3)

            if len(guns) != 0:
                print('Gun Detected!!')
                gun_exit = True
                is_locked = True
                msg1 = "Gun Detected!!"
            else:
                print('Safe!')
                msg1 = "Safe! Not have guns"

            if len(faces) != 0:
                print('People Detected!')
                msg2 = "People Detected!!"
                is_locked = True
            else:
                print('People Detected!')
                peoPle_exit = True
                msg2 = "Not People Safe!"
                
            if is_locked and (is_locked != is_lockedold):
                is_lockedold = True
                print("System Locked")
                GPIO.output(pinunlockGreenLED, GPIO.LOW)
                GPIO.output(pinlockRedLED, GPIO.HIGH)
                time.sleep(0.2)
            
            # Draw rectangle around
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Display text notification
                cv2.putText(img, 'People Detected', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            for (x, y, w, h) in guns:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # Display text notification
                cv2.putText(img, 'Gun Detected', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # Display the output
            cv2.imshow('img', img)
            cv2.waitKey()
            
            if gun_exit or peoPle_exit:
                # Get the current date and time
                thailand_timezone = pytz.timezone('Asia/Bangkok')
                timestamp = datetime.now(thailand_timezone).strftime("%Y-%m-%d %H:%M:%S")

                # Customize your notification message
                notification_message = f'Motion detected at {timestamp}!\nSecurity system triggered.\n{msg1}\n{msg2}'
                print(notification_message)
                # Convert image to bytes
                _, img_bytes = cv2.imencode('.jpg', img)
                
                r = requests.post(url, headers=headers, data={'message': notification_message}, 
                                  files={'imageFile': ('image.jpg', img_bytes.tobytes(), 'image/jpeg')})
                print(r.text)

                time.sleep(0.2)
                previousstate = 1
                
        elif currentstate == 0 and previousstate == 1:
            print(" Ready")
            previousstate = 0
            time.sleep(0.01)
            
except KeyboardInterrupt:
    print(" Quit")
    GPIO.cleanup()
