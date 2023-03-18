# CloudBasedFaceAttendace
This is a level up from my FaceAttendance project; here I've integrated cloud computing (aws), so that virtual servers can handle the entire storage and analysis portion; as a result, we no longer require any owned physical storage for the system's operation.

Additional library used:

    install boto3 (pip3 install cmake)
    install csv (pip3 install dlib)
    install keyboard
<hr>

In this project, I used a straightforward yet effective facial recognition algorithm which uses the HOG method to detect faces on the given picture. Afterwards, it detected 68 specific points on the face called the landmark which helped to locate the face regardless of the angle or position in the picture. The next step was construct Deep CNN which identified 128 facial encodings that help in uniquely identify the facial features.

Boto3 python sdk helps in fetching, quering and storing data, Attends images are stored in s3 it will fetch the images for comparsion and then When the face is identified and recognized, we mark the attendance and upload the results in S3 Bucket inside as object file. The file is saved inside the directories in hirearcy format of year, month and date (necessarily in that order) so as to enable users a proper way to find the files containing attendance.
