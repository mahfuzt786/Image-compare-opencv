from flask import Flask, request, render_template, send_from_directory, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import cv2
from shutil import copy2
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
trainedImagePath = os.path.join(APP_ROOT, "train")
TRAIN_FOLDER_mid = os.path.join(APP_ROOT, "trainSmall")
UPLOAD_FOLDER = os.path.join(APP_ROOT, "uploads")
POSTER_FOLDER = os.path.join(APP_ROOT, "poster")
POSTER_SMALL = os.path.join(APP_ROOT, "posterSmall")
POSTER_MID = os.path.join(APP_ROOT, "posterMid")

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'bmp'])

if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)

if not os.path.isdir(trainedImagePath):
        os.mkdir(trainedImagePath)

app = Flask(__name__)
#app.debug = True
app.secret_key = "super_secret_key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['POSTER_FOLDER'] = POSTER_FOLDER
app.config['POSTER_SMALL']  = POSTER_SMALL
app.config['POSTER_MID']  = POSTER_MID
app.config['TRAIN_FOLDER']  = trainedImagePath
app.config['TRAIN_FOLDER_mid']  = TRAIN_FOLDER_mid
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

## function to check allowed filetype
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## function to image resize
def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]
    
    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image    

    # # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # # otherwise, the height is None
    else:
    #     # calculate the ratio of the width and construct the
    #     # dimensions
    #     r = width / float(w)
    #     dim = (width, int(h * r))
        if w > 1200:
            dim = (int(w/1.5), int(h/1.5))
        else:
            dim = (w, h)
    
    # resize the image
    resized = cv2.resize(image, dim, interpolation = inter)

    # return the resized image
    return resized

## function to check image matching and return matching values
def computeImage(img1, img2):
    # Initiate SIFT detector
    # sift = cv2.SIFT()
    sift = cv2.xfeatures2d.SIFT_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = sift.detectAndCompute(img1,None)
    kp2, des2 = sift.detectAndCompute(img2,None)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=200)   # or pass empty dictionary

    flann = cv2.FlannBasedMatcher(index_params,search_params)

    matches = flann.knnMatch(des1,des2,k=2)

    # Need to draw only good matches, so create a mask
    matchesMask = [[0,0] for i in range(len(matches))]

    # ratio test as per Lowe's paper
    matching_points = 0
    total_points = 0
    for i,(m,n) in enumerate(matches):
        # if m.distance < 0.7*n.distance:
        if m.distance < 0.76*n.distance:
            matchesMask[i]=[1,0]
            matching_points = matching_points + 1
        total_points = total_points + 1

    matching_percentage = (matching_points * 100) / total_points

    return matching_percentage

## display home page and send required parameters
@app.route('/')
@app.route('/index')
def index():
    ## Train Images
    path, dirs, files = next(os.walk(trainedImagePath))
    file_count = len(files)
    image_names = os.listdir('./train')

    ## Poster Images
    pathUp, dirsUp, filesUp = next(os.walk(POSTER_FOLDER))
    file_countUp = len(filesUp)
    image_namesUp = os.listdir('./poster')

    return render_template('imageAI.html', filecount=file_count, files=files, image_names=image_names, filecountUp=file_countUp, image_namesUp=image_namesUp)

## display home page and send required parameters
@app.route('/select')
def select():
    ## Train Images
    path, dirs, files = next(os.walk(trainedImagePath))
    file_count = len(files)
    image_names = os.listdir('./train')

    ## Poster Images
    pathUp, dirsUp, filesUp = next(os.walk(POSTER_FOLDER))
    file_countUp = len(filesUp)
    image_namesUp = os.listdir('./poster')

    return render_template('compareAI.html', filecount=file_count, image_names=image_names, filecountUp=file_countUp, image_namesUp=image_namesUp)

## upload train images as well as check for existance
@app.route("/upload", methods=['POST'])
def upload():
    target  = os.path.join(APP_ROOT, 'uploads/')
    trained = os.path.join(APP_ROOT, 'train/')
    #print(request.url)
    if not os.path.isdir(target):
            os.mkdir(target)
    # else:
    #     flash("Couldn't create upload directory: {}".format(target))
    
    if not os.path.isdir(trained):
            os.mkdir(trained)

    if request.method == 'POST':
         # check if the post request has the file part
        if 'fileToUpload' not in request.files:
            flash('No file Selected..')
            return redirect(url_for('index')) #redirect(request.url)

        # file = request.files['fileToUpload']
        fileToUpload = request.files.getlist('fileToUpload')
        
        alreadyTrained = 0
        lessSize = 0
        for file in fileToUpload :
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                destinationTrain = os.path.join(app.config['TRAIN_FOLDER_mid'], filename)
                file.save(destination)
                copy2(destination, destinationTrain)
                ## after upload to 'uploads' folder check for duplicates
                #img1 = cv2.imread(destination, 0)             # queryImage
                #imgT = cv2.imread(destination)                  # queryImage
                imgT = cv2.imread(destinationTrain)                  # queryImage
                (h, w) = imgT.shape[:2]
                if w < 400:
                    lessSize += 1
                else :
                    ## resize the image
                    imgT = image_resize(imgT, height = 250)
                    # save the resized image
                    #cv2.imwrite(destination, imgT)
                    #img1 = cv2.imread(destination)
                    cv2.imwrite(destinationTrain, imgT)
                    img1 = cv2.imread(destinationTrain)

                    #alreadyTrained = duplicateTrain(destination, trained, img1, alreadyTrained)
                    alreadyTrained = duplicateTrain(destinationTrain, trained, img1, alreadyTrained)
            else:
                return 'File not allowed'

        if alreadyTrained > 0:
            flash('{} Image(s) already Trained.'.format(alreadyTrained))
        if lessSize > 0:
            flash('{} Image(s) are of less resolutions. Min. width is 400px.'.format(lessSize))

        return redirect(url_for('index'))

    return 'Error'
    
# Function to check matched images with the big poster
@app.route("/uploaded", methods=['POST'])
def uploaded():
    target      = os.path.join(APP_ROOT, 'uploads/')
    poster      = os.path.join(APP_ROOT, 'poster/')
    posterMid = os.path.join(APP_ROOT, 'posterMid/')
    
    if not os.path.isdir(target):
            os.mkdir(target)
    # else:
    #     flash("Couldn't create upload directory: {}".format(target))
    
    if not os.path.isdir(poster):
            os.mkdir(poster)
    
    if request.method == 'POST':
         # check if the post request has the file part
        if 'fileToUpload' not in request.files:
            flash('No file Selected...')
            return redirect(url_for('index')) #redirect(request.url)

        #file = request.files['fileToUpload']
        fileToUpload = request.files.getlist('fileToUpload')
        
        alreadyTrainedUp  = 0
        lessSize          = 0
        for file in fileToUpload :
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename            = secure_filename(file.filename)
                destination         = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                destinationSmall    = os.path.join(app.config['POSTER_SMALL'], filename)
                file.save(destination)
                #print(destination)
                copy2(destination, destinationSmall)
                ## after upload to 'uploads' folder check for matching
                #img1 = cv2.imread(destination, 0)             # queryImage
                #img1 = cv2.imread(destination)                  # queryImage
                ## resize the image            
                #img1 = image_resize(img1, height = 900)
                # save the resized image
                #cv2.imwrite(destination, img1)
                
                imgB = cv2.imread(destination)                  # queryImage

                # For Compare with trained images need bigger resolutions
                (h, w) = imgB.shape[:2]
                if w < 900:
                    lessSize += 1
                else :
                    ## resize the image
                    imgB = image_resize(imgB, width= 960)
                    # save the resized image
                    cv2.imwrite(destination, imgB)
                #     img1 = cv2.imread(destination)

                imgT = cv2.imread(destinationSmall)                  # queryImage
                (hs, ws) = imgT.shape[:2]
                if ws > 900:
                    imgT = image_resize(imgT, height= 500)
                    # save the resized image
                    cv2.imwrite(destinationSmall, imgT)
                    img1 = cv2.imread(destinationSmall)
                    
                    #alreadyTrainedUp = duplicate(destination, poster, img1, alreadyTrainedUp)
                    alreadyTrainedUp = duplicate(destination, poster, destinationSmall, posterMid, img1, alreadyTrainedUp)
                # if not os.listdir("./poster"):
                #     copy2(destination, poster)
                # else:
                #     ## Find All images from the train folder (JPEG, JPG, PNG, GIF and BMP)
                #     for file in os.listdir("./poster"):
                #         if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg') or file.lower().endswith('.png') or file.lower().endswith('.gif') or file.lower().endswith('.bmp'):
                #             newImage = os.path.join('poster/', file)
                #             print(newImage)
                #             print('--------')
                #             img2 = cv2.imread(newImage)     # trainImage
                #             returnValue = computeImage(img1, img2)
                            
                #             if returnValue >= 75:
                #                 alreadyTrainedUp += 1                 
                #                 # flash('Image already Uploaded.')
                #                 # return redirect(url_for('index'))
                #                 ## return '<h1> Image already trained.. </h1> <br/> <h3><a href="/"> Back to Home </a></h3>'
                #             else:
                #                 destFile.append(destination)
                #     # copy2(destination, poster)
                #return redirect(url_for('index'))
            else:
                return 'File not allowed'

        if alreadyTrainedUp > 0:
            flash('{} Image(s) already Uploaded.'.format(alreadyTrainedUp))
        if lessSize > 0:
            flash('{} Image(s) are of less resolutions. Min. width of group poster is 900px.'.format(lessSize))
        return redirect(url_for('index'))

    return 'Error'

# def duplicate(destinationSmall, posterSmall, destination, poster, img1, alreadyTrainedUp):
def duplicate(destination, poster, destinationSmall, posterMid, img1, alreadyTrainedUp):
    if not os.listdir("./posterMid"):
        copy2(destinationSmall, posterMid)
        copy2(destination, poster)
    else:
        ## Find All images from the train folder (JPEG, JPG, PNG, GIF and BMP)
        for file in os.listdir("./posterMid"):
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg') or file.lower().endswith('.png') or file.lower().endswith('.gif') or file.lower().endswith('.bmp'):
                newImage = os.path.join('posterMid/', file)
                # img2 = cv2.imread(newImage, 0)     # trainImage
                img2 = cv2.imread(newImage)     # trainImage
                returnValue = computeImage(img1, img2)
                
                if returnValue >= 75:
                    alreadyTrainedUp += 1
                    return alreadyTrainedUp
        
        copy2(destinationSmall, posterMid)
        copy2(destination, poster)

    return alreadyTrainedUp

# def duplicate(destination, poster, img1, alreadyTrainedUp):
#     if not os.listdir("./poster"):
#         copy2(destination, poster)
#         #copy2(destinationSmall, posterSmall)
#     else:
#         ## Find All images from the train folder (JPEG, JPG, PNG, GIF and BMP)
#         for file in os.listdir("./poster"):
#             if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg') or file.lower().endswith('.png') or file.lower().endswith('.gif') or file.lower().endswith('.bmp'):
#                 newImage = os.path.join('poster/', file)
#                 # img2 = cv2.imread(newImage, 0)     # trainImage
#                 img2 = cv2.imread(newImage)     # trainImage
#                 returnValue = computeImage(img1, img2)
#                 print(returnValue)
#                 if returnValue >= 75:
#                     alreadyTrainedUp += 1
#                     return alreadyTrainedUp
#                 # else:
#                 #     copy2(destination, poster)
        
#         copy2(destination, poster)
#         #copy2(destinationSmall, posterSmall)

#     return alreadyTrainedUp

def duplicateTrain(destination, trained, img1, alreadyTrained):
    if not os.listdir("./train"):
        copy2(destination, trained)
    else:
        ## Find All images from the train folder (JPEG, JPG, PNG, GIF and BMP)
        for file in os.listdir("./train"):
            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg') or file.lower().endswith('.png') or file.lower().endswith('.gif') or file.lower().endswith('.bmp'):
                newImage = os.path.join('train/', file)
                # img2 = cv2.imread(newImage, 0)     # trainImage
                img2 = cv2.imread(newImage)     # trainImage
                returnValue = computeImage(img1, img2)
                
                if returnValue >= 75 :
                    alreadyTrained += 1
                    return alreadyTrained
    
        copy2(destination, trained) 
        #move(des..., tra...) to be implemented later

    return alreadyTrained

# Function to check matched images with the big poster
@app.route("/compare", methods=['POST'])
def compare():
    if request.method == 'POST':
        trainSelectedImg    = eval(request.form['trainSelected'])
        posterSelectedImg   = eval(request.form['posterSelected'])

        if len(trainSelectedImg) > 0 and len(posterSelectedImg) > 0:
            imgListS            = []
            imgValueS           = []
            imgListNoS          = []
            imgValueNoS         = []
            matchedSize         = 0
            for i in range (0, len(posterSelectedImg)):
                destination = os.path.join(app.config['POSTER_FOLDER'], posterSelectedImg[i])
                destinationMid = os.path.join(app.config['POSTER_MID'], posterSelectedImg[i])
                #print(destination)
                ## load the image from 'poster' folder check for matching
                img1 = cv2.imread(destination)             # queryImage
                #img1 = cv2.imread(destination)                  # queryImage
                
                # TO BE IMPLEMENTED FOR COMPARE FUNCTION
                imgList         = []
                imgValue        = []
                imgListNo       = []
                imgValueNo      = []
                ## Find All images from the train folder
                for file in trainSelectedImg: #os.listdir("./train"):
                    if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg') or file.lower().endswith('.png') or file.lower().endswith('.gif') or file.lower().endswith('.bmp'):
                        newImage = os.path.join('train/', file)
                        #print(newImage)
                        img2 = cv2.imread(newImage)     # trainImage
                        returnValue = computeImage(img2, img1)

                        if returnValue >= 1.63 :
                            matchedSize += 1

                        # if returnValue >= 1.63 :
                        imgList.append(file)
                        imgValue.append(str(round(returnValue, 2)))
                            #print(newImage)
                            #print(returnValue)
                        # else:
                        #     imgListNo.append(file)
                        #     imgValueNo.append(str(round(returnValue, 2)))
                
                # Calculate total matched trained images
                # matchedSize += len(imgList)
                # Delete image from poster folder
                os.remove(destination)
                os.remove(destinationMid)

                imgListS.append(imgList)
                imgValueS.append(imgValue)
                imgListNoS.append(imgListNo)
                imgValueNoS.append(imgValueNo)
            
            ## display output 
            return render_template("output.html", matchedSize=matchedSize, matchedImage=imgListS, nomatchedImage=imgListNoS, matchedValue=imgValueS, nomatchedValues=imgValueNoS, image_poster=posterSelectedImg, image_train=trainSelectedImg)
        else:
            flash('No Image to Compare')
            return redirect(url_for('index'))

    return 'Error'

# Function to check matched images with the big poster
@app.route("/delete", methods=['POST'])
def delete():
    if request.method == 'POST':
        deleteSelectedImg       = request.form['deleteImage']
        deleteFrom              = request.form['deleteFrom']
        
        if deleteFrom == 'poster' :
            destination    = os.path.join(app.config['POSTER_FOLDER'], deleteSelectedImg)
            destinationMid = os.path.join(app.config['POSTER_MID'], deleteSelectedImg)
        else :
            destination = os.path.join(app.config['TRAIN_FOLDER'], deleteSelectedImg)
            destinationMid = os.path.join(app.config['TRAIN_FOLDER_mid'], deleteSelectedImg)
        
        # Delete image from folder
        os.remove(destination)
        os.remove(destinationMid)
            
        flash('Image Deleted')
        return redirect(url_for('index'))

    return 'Error'

## to display output images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

## to display Trained Images
@app.route('/train/<filename>')
def send_image(filename):
    return send_from_directory("train", filename)

## to display Poster Images
@app.route('/poster/<filename>')
def poster_image(filename):
    return send_from_directory("poster", filename)

# @app.route('/output')
# def get_gallery(imgList):
#     print(imgList)
#     return render_template("output.html", image_names=imgList)

if __name__ == "__main__":
    app.run(debug=True)
    #app.run(port=4996, host='0.0.0.0')
