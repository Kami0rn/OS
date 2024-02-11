# my line token
# wKmy2APAY7sfT9Vrnqx3aI7garZkz51FMwHItR8wdll

import RPi.GPIO as GPIO
import time
import requests
from datetime import datetime
import pytz

import subprocess
import cv2

# face_recognition
import face_recognition
import os
from IPython.display import Image,display

# detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

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

def read_img(path):
    img = cv2.imread(path)
    (h, w) = img.shape[:2]
    width = 500
    ratio = width / float(w)
    height = int(h * ratio)
    return cv2.resize(img, (width, height))

known_encodings = []
known_names = []
known_dir = 'face/HouseHold'
for file in os.listdir(known_dir):
    img = read_img(known_dir + '/' + file)
    img_enc = face_recognition.face_encodings(img)[0]
    known_encodings.append(img_enc)
    known_names.append(file.split('.')[0])

is_locked = False
is_lockedold = True
houseHold_exit = False
peoPle_exit = False
msg1 = ""
msg2 = ""

try:
    print("Waiting for PIR to settle ...")
    
    while GPIO.input(pinpir) == 1:
        currentstate = 0
    print(" Ready")
    for x in range(0, 5):
        GPIO.output(pinredled, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(pinredled, GPIO.LOW)
        GPIO.output(pinblueled, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(pinblueled, GPIO.LOW)
        time.sleep(0.2)
        
    while True:
        if is_locked and (is_locked != is_lockedold):
            is_lockedold = True
            print("System Locked")
            GPIO.output(pinunlockGreenLED, GPIO.LOW)
            GPIO.output(pinlockRedLED, GPIO.HIGH)
            time.sleep(0.2)
        if not is_locked and(is_locked != is_lockedold):
            is_lockedold = False
            print("System UnLocked")
            GPIO.output(pinunlockGreenLED, GPIO.HIGH)
            GPIO.output(pinlockRedLED, GPIO.LOW)
            time.sleep(0.2)
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
            
            # Detect 
            faces = face_cascade.detectMultiScale(grayFace, 1.2, 4)

            if len(faces) != 0:
                print('People Detected!')
                peoPle_exit = True
            else:
                print('Not People, Safe!')
                peoPle_exit = False
                
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
            #img.save('Detected.jpg')
            cv2.imshow('img', img)
            cv2.waitKey()
            
            if peoPle_exit:
                print("peoPle_exit")
                img_enc = face_recognition.face_encodings(img)

                if img_enc:  # Check if face encoding is available
                    results = face_recognition.compare_faces(known_encodings, img_enc[0])

                    recognized = False
                    for i in range(len(results)):
                        if results[i]:
                            name = known_names[i]
                            recognized = True
                            (top, right, bottom, left) = face_recognition.face_locations(img)[0]
                            cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
                            cv2.putText(img, name, (left+2, bottom+20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
                    #img.save('Recognite.jpg')
                    cv2.imshow('img', img)
                    cv2.waitKey()
                    
                    if recognized:
                        houseHold_exit = True
                        is_locked = False
                        msg1 = "Welcome " + name
                        print(f"Recognized: {name}")
                       
                    else:
                        print("Unknown")
                        is_locked = True
                        msg1 = "Have stranger, Who? !"
                    # Get the current date and time
                    thailand_timezone = pytz.timezone('Asia/Bangkok')
                    timestamp = datetime.now(thailand_timezone).strftime("%Y-%m-%d %H:%M:%S")

                    # Customize your notification message
                    notification_message = f'Motion detected at {timestamp}!\nSecurity system triggered.\n{msg1}'
                    print(notification_message)
                    # Convert image to bytes
                    _, img_bytes = cv2.imencode('.jpg', img)
                        
                    r = requests.post(url, headers=headers, data={'message': notification_message}, 
                                          files={'imageFile': ('image.jpg', img_bytes.tobytes(), 'image/jpeg')})
                    print(r.text)
                         
                    if is_locked and (is_locked != is_lockedold):
                        is_lockedold = True
                        print("System Locked")
                        GPIO.output(pinunlockGreenLED, GPIO.LOW)
                        GPIO.output(pinlockRedLED, GPIO.HIGH)
                        time.sleep(0.2)
                        
                    time.sleep(0.2)
                    
                    
                else:
                    print("No face detected")                
               
                previousstate = 1
                
        elif currentstate == 0 and previousstate == 1:
            print(" Ready")
            previousstate = 0
            time.sleep(0.01)
            
except KeyboardInterrupt:
    print(" Quit")
    GPIO.cleanup()
