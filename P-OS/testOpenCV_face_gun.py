import cv2

# Load the cascade
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
gun_cascade = cv2.CascadeClassifier('classifier/cascade.xml')

# Read the input image
img = cv2.imread('gg.png')

gun_exit = False
PeoPle_exit = False
# Convert into grayscale
grayFace = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
grayGun = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Detect 
faces = face_cascade.detectMultiScale(grayFace, 1.1, 4)
guns = gun_cascade.detectMultiScale(grayGun, 1.01, 3)

if len(guns) != 0:
    print('Gun!!!')
    gun_exit = True
    msg1 = "Gun Detected!!"
else:	
    print('Safe!')
    msg1 = "Safe!"

if len(faces) != 0:
    print('People Detected!')
    msg2 = "People Detected!!"
else:	
    print('People Detected!')
    PeoPle_exit = True
    msg2 = "Safe!"

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