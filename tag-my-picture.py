import boto3
from PIL import Image
import os
import io
import uuid
import shutil
import mimetypes

# You should chance these variables

collection_id='Faces4Photoprism'        # doesn't matter, name it what you like
collection_filename="./collection.txt"  # we store all faces sent to AWS Rekognition locally so we don't do it twice
translation_filename="./translate.txt"  # we store all translated labels locally, so we don't need to translate twice

path_to_temp="./temp/"                  # a temp folder, please create
path_to_faces="./pics/"                 # the folder where the faces of the known persons are stored. Please see README.md
path_to_unknown_faces="./_unknown/"     # the folder where unknown faces are stored. Please see README.md
path_to_pictures="/mnt/Dropbox/Camera Uploads/"     # the folder where the pictures to process are stored

### 

def limit_img_size(img_filename, img_target_filename, target_filesize, tolerance=5):
    # code from: https://stackoverflow.com/questions/52940369/is-it-possible-to-resize-an-image-by-its-bytes-rather-than-width-and-height
    img = img_orig = Image.open(img_filename)
    aspect = img.size[0] / img.size[1]

    while True:
        with io.BytesIO() as buffer:
            img.save(buffer, format="JPEG")
            data = buffer.getvalue()
        filesize = len(data)    
        size_deviation = filesize / target_filesize
        print("size: {}; factor: {:.3f}".format(filesize, size_deviation))

        if size_deviation <= (100 + tolerance) / 100:
            # filesize fits
            with open(img_target_filename, "wb") as f:
                f.write(data)
            break
        else:
            # filesize not good enough => adapt width and height
            # use sqrt of deviation since applied both in width and height
            new_width = img.size[0] / size_deviation**0.5    
            new_height = new_width / aspect
            # resize from img_orig to not lose quality
            img = img_orig.resize((int(new_width), int(new_height)))

def resize_image(photo,maxsize,overwrite=False):
    size=os.path.getsize(photo)
    if size>maxsize:
        print("Have to resize image. It is "+str(size))
        if not overwrite:
            new_filename=path_to_temp+uuid.uuid4().hex+".jpg"
        else:
            new_filename=photo
        limit_img_size(photo,new_filename,maxsize)                
        size=os.path.getsize(new_filename)
        print("Image resized. New size "+str(size))
        return new_filename
    else:
        return photo

def save_collection(collected_faces):
    with open(collection_filename, "w") as f:
        for face in collected_faces:
            f.write(face+"\n")

def load_collection():
    collected_faces=[]
    with open(collection_filename) as f:
        for cnt, line in enumerate(f):
            collected_faces.append(line.replace("\n",""))
    return collected_faces

def save_translate(wortliste):
    with open(translation_filename, "w") as f:
        for key in wortliste:
            f.write(key+";"+wortliste[key]+"\n")

def load_translate():
    wortliste={}
    with open(translation_filename) as f:
        for cnt, line in enumerate(f):
            en,de=line.split(";")
            wortliste[en.replace("\n","")]=de.replace("\n","")
    return wortliste

def read_filelist(pfad):
    onlyfiles = [f for f in os.listdir(pfad) if os.path.isfile(os.path.join(pfad, f))]
    return onlyfiles

def list_faces_in_collection(collection_id):
    maxResults=10
    faces_count=0
    tokens=True

    response=client.list_faces(CollectionId=collection_id,
                               MaxResults=maxResults)

    print('Faces in collection ' + collection_id)
 
    while tokens:

        faces=response['Faces']

        for face in faces:
            print (face)
            faces_count+=1
        if 'NextToken' in response:
            nextToken=response['NextToken']
            response=client.list_faces(CollectionId=collection_id,
                                       NextToken=nextToken,MaxResults=maxResults)
        else:
            tokens=False
    return faces_count   

def search_faces(photo,collection_id):
    img = Image.open(photo) # this is our original picture to work with

    photo_work=resize_image(photo,4500000) # if necessary we resize the picture in a temporary file
    imageSource=open(photo_work,'rb')
    SourceImage={'Bytes': imageSource.read()}

    response=client.detect_faces(Image=SourceImage,Attributes=['ALL'])
    
    found_persons=[]

    for face in response['FaceDetails']:
        print(face)
        box = face['BoundingBox']
        left = img.width * box['Left']
        top = img.height * box['Top']
        width = img.width * box['Width']
        height = img.height * box['Height']
        cropped = img.crop( ( left, top, left + width, top + height ) ) 
        cropped.show()
        temp_filename=path_to_temp+uuid.uuid4().hex+".jpg"
        cropped.save(temp_filename)
        temp_filename=resize_image(temp_filename,4500000,overwrite=True) # just to be sure to get no bigger pictures
        results=search_face(temp_filename,collection_id)
        if results:
            for result in results:
                found_persons.append(result)

    return found_persons

def search_face(photo,collection_id):
    threshold = 50  # how sure the algorithm has to be
    maxFaces=1      # how many results - we only want one

    photo=resize_image(photo,4500000,overwrite=True) # just to be sure, the temporary face picture should not be bigger

    client=boto3.client('rekognition')

    imageSource=open(photo,'rb')
    SourceImage={'Bytes': imageSource.read()}

    try:
        response=client.search_faces_by_image(CollectionId=collection_id,
                                    Image=SourceImage,
                                    FaceMatchThreshold=threshold,
                                    MaxFaces=maxFaces)
    except:
        print("Error searching for face. Skipping.")
        return


    faceMatches=response['FaceMatches']
    found_faces=[]
    print ('Matching faces')
    for match in faceMatches:
        #print(match)
        print("Match for "+photo)
        print ('FaceId:' + match['Face']['FaceId'])
        print ("Who: " + match['Face']['ExternalImageId'])
        print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
        print
        found_faces.append(match['Face']['ExternalImageId'])

    if len(faceMatches)==0:
        print("No matches for "+photo)
        head, tail = os.path.split(photo)
        shutil.move(photo, path_to_unknown_faces+tail)
        
    return set(found_faces)


def add_faces_to_collection(photo,photo_id,collection_id):
    imageSource=open(photo,'rb')
    SourceImage={'Bytes': imageSource.read()}

    response=client.index_faces(CollectionId=collection_id,
                                Image=SourceImage,
                                ExternalImageId=photo_id,
                                MaxFaces=1,
                                QualityFilter="AUTO",
                                DetectionAttributes=['ALL'])

    print ('Results for ' + photo) 	
    print('Faces indexed:')						
    for faceRecord in response['FaceRecords']:
         print('  Face ID: ' + faceRecord['Face']['FaceId'])
         print('  Location: {}'.format(faceRecord['Face']['BoundingBox']))

    print('Faces not indexed:')
    for unindexedFace in response['UnindexedFaces']:
        print(' Location: {}'.format(unindexedFace['FaceDetail']['BoundingBox']))
        print(' Reasons:')
        for reason in unindexedFace['Reasons']:
            print('   ' + reason)
    return len(response['FaceRecords'])

def update_collection(collected_faces):
    dirlist=[x[0] for x in os.walk(path_to_faces)]
    for onedir in dirlist:
        person_name=onedir.replace(path_to_faces,"")
        print("Person: "+person_name)
        if person_name!="":
            allfiles=read_filelist(onedir) # get all image in the folder for one person
            for onefile in allfiles: # iterate over all the images 
                filename=onedir+"/"+onefile
                print(filename)
                if not filename in collected_faces:
                    filename=resize_image(filename,4500000,overwrite=True)
                    add_faces_to_collection(filename,person_name,collection_id)
                    collected_faces.append(filename)
                    print("Added face "+filename)
                else:
                    print("Already in the collection: "+filename)
    return collected_faces

# Init
client=boto3.client('rekognition')
translate = boto3.client(service_name='translate', region_name='eu-west-1', use_ssl=True)
mimetypes.init()

# Create a collection for Face Rekognition
try:
    response=client.create_collection(CollectionId=collection_id)
    print("Created collection "+collection_id)
except:
    print("Can't create. Probably exists.")

# Read the already collected faces from local copy, if possible
try:
    collected_faces=load_collection()
except:
    print("Cant' load face collection file.")
    collected_faces=[]

# load all previously translated labels, so we don't call the api again
try:
    translated=load_translate()
except :
    print("Can't load translation file. Starting from scratch.")
    translated = {}

# Add new faces to the collection
collected_faces=update_collection(collected_faces)

# Save collected faces to  local copy
save_collection(collected_faces)

# if you want to see what is inside your collection
# print (list_faces_in_collection(collection_id))

# process all pictures in the folder path_to_pictures
dateien=read_filelist(path_to_pictures)

for datei in dateien:
    photo = path_to_pictures+datei
    print(photo)
    mimestart = mimetypes.guess_type(photo)[0]

    if mimestart != None:
        mimestart = mimestart.split('/')[0]

        if mimestart == 'image': # or mimestart == 'video' - but at the moment we don't analyse video 
            print("File is an image.")

            photo_work=resize_image(photo,4500000) # we get an working photo of maxsize 4,5MB (AWS maximum is 5MB)

            # we ask Amazon Rekognition for the labels of the picture
            with open(photo_work, 'rb') as image:
                response = client.detect_labels(Image={'Bytes': image.read()},  MaxLabels=50)

            # There are labels and parents, we take them both for our exif keywords
            label_lst = []
            for label in response['Labels']:
                label_lst.append(label['Name'])
                
            for label in response['Labels']:
                for parents in label['Parents']:
                    label_lst.append(parents['Name'])

            # we make the results a set to get every label only once
            labels_en=set(label_lst)

            # now we translate our labels
            labels_de=[]
            for label_en in labels_en:
                if label_en in translated:
                    print("Word is already translated. We use the saved translation.")
                    # add the translation to our result for the picture
                    labels_de.append(translated[label_en])
                else:
                    print("Ask Amazon Translate for translation.")
                    new_word=translate.translate_text(Text=label_en,SourceLanguageCode="en", TargetLanguageCode="de")
                    new_word=new_word['TranslatedText']
                    # we don't want these words in our labels
                    new_word=new_word.replace("Der ","")
                    new_word=new_word.replace("Die ","")
                    new_word=new_word.replace("Das ","")
                    new_word=new_word.replace("der ","")
                    new_word=new_word.replace("die ","")
                    new_word=new_word.replace("das ","")
                    # add the translation to our translated words
                    translated[label_en]=new_word
                    # add the translation to our result for the picture
                    labels_de.append(new_word)
                    print("The transaltion for "+label_en+" is "+new_word)

            print(labels_de)
            # now we call exiftool to add the keywords
            cmdline=""
            for label in set(labels_de):
                cmdline=cmdline+" -iptc:keywords-='"+label+"' -iptc:keywords+='"+label+"'"
            if cmdline!="":
                print(os.system("exiftool -overwrite_original "+cmdline+" '"+photo+"'"))

            if "Person" in set(labels_de) or "Mensch" in set(labels_de):
                # search a picture
                found_persons=search_faces(photo_work,collection_id)

                # write result to picture
                cmdline=""
                for person in found_persons:
                    cmdline=cmdline+" -iptc:keywords-='"+person+"' -iptc:keywords+='"+person+"'"
                if cmdline!="":
                    print(os.system("exiftool -overwrite_original "+cmdline+" '"+photo+"'"))
        else:
            print("No media type.")

print("Save translations.")
save_translate(translated)