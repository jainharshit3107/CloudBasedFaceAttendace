import cv2
import face_recognition
from _datetime import datetime
from datetime import date
import boto3
from PIL import Image
import numpy as np
import csv
import sys
import keyboard

ACCESS_KEY_ID = str(input("Please provide the Key ID to start: "))
SECRET_ACCESS_KEY = str(input("Please provide the credentials to start: "))

images = []
attendeeNames = []
myList = []
globalName = []
checkName = []
month_names = ["JAN", "FEB", "MARCH", "APRIL", "MAY", "JUNE", "JULY",
                   "AUG", "SEP", "OCT", "NOV", "DEC"]
bucket_name = "faceattendance-h2pc"
s3 = boto3.resource('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)
s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY)

def year_fun():
    year_list = []
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = response.get("Contents")
    if files:
        for file in files:
            year_list.append(file['Key'])
        return year_list
    return year_list

def month_fun():
    month_list = []
    todays_date = date.today()
    my_bucket = s3.Bucket(bucket_name)
    for object_summary in my_bucket.objects.filter(Prefix=f"{todays_date.year}/"):
        month_list.append(object_summary.key)
    return month_list
def day_fun():
    day_list = []
    todays_date = date.today()
    my_bucket = s3.Bucket(bucket_name)
    for object_summary in my_bucket.objects.filter(Prefix=f"{todays_date.year}/{month_names[todays_date.month-1]}"):
        day_list.append(object_summary.key)
    return day_list

def create_folder():
    todays_date = date.today()
    year = f"{todays_date.year}"
    month = f"{todays_date.year}/{month_names[todays_date.month-1]}"
    day = f"{todays_date.year}/{month_names[todays_date.month-1]}/{todays_date.day}"
    year_list = year_fun()
    if year not in year_list:
        folder_name = year
        s3_client.put_object(Bucket=bucket_name, Key=(folder_name+'/'))
    month_list = month_fun()
    if month not in month_list:
        folder_name = month
        s3_client.put_object(Bucket=bucket_name, Key=(folder_name+'/'))
    day_list = day_fun()
    if day not in day_list:
        folder_name = day
        s3_client.put_object(Bucket=bucket_name, Key=(folder_name+'/'))


def upload_file(csv_name):
    create_folder()
    todays_date = date.today()
    s3_client.upload_file(
        Filename=csv_name,
        Bucket=bucket_name,
        Key=f"{todays_date.year}/{month_names[todays_date.month-1]}/{todays_date.day}/{csv_name}.csv"
    )

def create_csv(globalName):
    fields = ['Name', 'TimeStamp']
    todays_date = date.today()
    now = datetime.now()
    dtString = now.strftime('%H-%M')
    csv_name = f'Attendance-{dtString}'
    with open(f'Attendance-{dtString}', 'w') as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(globalName)
    upload_file(csv_name)



def list_s3_files_using_client():
    bucket_name = "attendefaces"
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    files = response.get("Contents")
    for file in files:
        attendeeNames.append(file['Key'])
        print(f"Attendees_name: {file['Key'][:-4]}")

list_s3_files_using_client()

def read_image_from_s3():
    #create a new bucket for the faces
    bucket = "attendefaces"
    bucket = s3.Bucket(bucket)
    for key in attendeeNames:
        object = bucket.Object(key)
        response = object.get()
        file_stream = response['Body']
        im = Image.open(file_stream)
        images.append(np.array(im))

read_image_from_s3()


def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # face_encodings gives 128 measurements to face to uniquely identify it
        # it generates nearly the same numbers (measurement) when looking at two different pictures of the same person.
        enMy = face_recognition.face_encodings(img)[0]
        # in case you want to see 128 measurements uncomment below print
        # print(enMy)
        encodeList.append(enMy)
    return encodeList

def appendNames(name):
    if name not in checkName:
        nameList = []
        nameList.append(name)
        checkName.append(name)
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        nameList.append(f"{dtString}")
        return nameList
    return 0


encodeList = findEncodings(images)
print('Ready To Start')
# Opening the default camera
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    # # resizing image for computational purpose (1/4 size)
    # imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Will output a tuple with 4 different points (location of face)
    facesCurFrame = face_recognition.face_locations(imgS)
    # To determine 128 measurements on face
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        # face_distance simply gives the difference between the known_face_encodings & face_encoding_to_check
        # compare_faces gives a difference list of face_distance <= tolerance
        matches = face_recognition.compare_faces(encodeList, encodeFace)
        faceDis = face_recognition.face_distance(encodeList, encodeFace)
        # print(faceDis)
        # Gives the index number from list(faceDis) of minimum value
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = attendeeNames[matchIndex][:-4].upper()
            # print(name)
            list1 = []
            # as we have resized the image before, now to change it in it's original form
            for i in faceLoc:
                list1.append(i*4)
            y1, x1, y2, x2 = faceLoc
            # for bounding the face with rectangle box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2-15), (x2, y2), (0, 255, 0), cv2.FILLED)
            # for putting the name below
            cv2.putText(img, name, (x2, y2+30), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            nameList = appendNames(name)
            if nameList != 0:
                globalName.append(nameList)
                print(globalName)


    if keyboard.is_pressed('Esc'):
        print("\nyou pressed Esc, so exiting...")
        create_csv(globalName)

        sys.exit(0)
    cv2.imshow('webcam', img)
    cv2.waitKey(1)



