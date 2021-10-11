from bs4 import BeautifulSoup
from urllib.parse import urlparse
from lxml import html
from PIL import Image
from mtcnn import MTCNN
from csv import DictWriter
from model import create_model
import matplotlib.pyplot as plt
import numpy as np
import requests
import os

site="https://www.project-a.com/"
savelocation=os.getcwd()+"/data"
direc=site[12:-5]
file_name=os.getcwd()+"/raw_data/summary_gender.csv"
summary={}
genmodel=create_model()
genmodel.load_weights(os.getcwd()+"/raw_data/my_model.h5")

def process_links(links):
    """ Function to process the list of links and filter required links."""
    links_list = []
    formats= ["jpg", "png", "gif", "jpeg"] 
    for link in links:
        if link[-3:].lower() in formats:
            links_list.append(link)
    return links_list  

def listing_pages(site):
    """ Function to find all relevant pages of a website"""
    resultsss=[]
    relevant_pages=["job", "about", "career", "jobs", "join", "team"]
    response = requests.get(site)
    soup = BeautifulSoup(response.text, 'html.parser')
    for x in soup.find_all("a"):  
        if "href" in x.attrs.keys():
            if x.string != None:
                if x.string != None and x.string.lower() in relevant_pages:
                    if 'http' not in x.attrs["href"]:
                        resultsss.append(site[:-1]+x.attrs["href"])
                    else:  resultsss.append(x.attrs["href"])    
                if x.span and len([s for s in relevant_pages if s in x.span.text.lower()])>0: 
                    if 'http' not in x.attrs["href"]:
                        resultsss.append(site[:-1]+x.attrs["href"])
                    else:  resultsss.append(x.attrs["href"])  
    return resultsss

def extracting_images(page):  
    """ Function to find all images links in a page"""    
    response = requests.get(page)
    tree = html.fromstring(response.text)    
    img = tree.xpath('//img/@src')
    links = tree.xpath('//a/@href')
    img_list = process_links(img)
    img_links = process_links(links)
    img_list.extend(img_links)
    return img_list

def save_image(image_link):
    """ Function to save a picture from a link in related folder"""
    if urlparse(image_link).scheme=="":
        image_link="https:"+image_link
    if urlparse(image_link).netloc=="":
        image_link=site+image_link
    img_request = requests.request('get', image_link, stream=True)
    if img_request.status_code==200:
        if image_link[-3:] != "svg" or int(img_request.headers["Content-Length"])>1000:
            img_content = img_request.content
            base=f"{savelocation}/{direc}/"
            if os.path.exists(base) is False:
                    os.makedirs(base)
            # with open(base+image_link.split('/')[-1], 'wb') as f:
            with open(base+urlparse(image_link).path.split('/')[-1], 'wb') as f:                
                byte_image = bytes(img_content)
                f.write(byte_image)
    return base

def draw_faces_quick(filename, result_list, pic):
    """ Function to save a crop of a face from a picture"""
    crop_=os.getcwd()+'/data/cropped/'
    data = plt.imread(filename)
    image_no = 1
    for i in range(len(result_list)):
        x1, y1, width, height = result_list[i]['box']
        x2, y2 = x1 + width, y1 + height
        fig1=plt.gcf()
        plt.axis('off')    
        try: plt.imshow(data[y1:y2, x1:x2])  #imgresult=
        except ValueError:
            pass
        print(filename)
        plt.show()    
        format=pic.split(".")[1]
        crop_path=crop_+direc+"/"+pic.strip(f".{format}")+"/"
        name=crop_path+"/face_"+str(image_no)
        if os.path.exists(crop_) is False:
            os.makedirs(crop_)
        if os.path.exists(crop_+direc+"/") is False:
            os.makedirs(crop_+direc+"/")
        if os.path.exists(crop_path) is False:
            os.makedirs(crop_path)
        fig1.savefig(f"{name}.jpg")
        image_no+=1

def process_and_predict(file):
    im = Image.open(file)
    width, height = im.size
    if width == height:
        im = im.resize((200,200), Image.ANTIALIAS)
    else:
        if width > height:
            left = width/2 - height/2
            right = width/2 + height/2
            top = 0
            bottom = height
            im = im.crop((left,top,right,bottom))
            im = im.resize((200,200), Image.ANTIALIAS)
        else:
            left = 0
            right = width
            top = 0
            bottom = width
            im = im.crop((left,top,right,bottom))
            im = im.resize((200,200), Image.ANTIALIAS)
            
    ar = np.asarray(im)
    ar = ar.astype('float32')
    ar /= 255.0
    ar = ar.reshape(-1, 200, 200, 3)
    return ar

pictures_treated=0
directory_processed=0
faces_num=[]
pictures_treated_wo_faces=0
picture_w_faces=0
male=0
female=0 

resultsss=listing_pages(site)
if resultsss !=[]:
    for s in resultsss:
        img_list=extracting_images(s)
        for x in img_list:
            base=save_image(x)
            
imlist=list(filter(os.path.isfile, [os.path.join(base, f) for f in os.listdir(base)]))

for x in imlist:
    if x.split(".")[1] == "png": 
        im1 = Image.open(x)
        x=x.split(".")[0]
        rgb_im = im1.convert('RGB')
        rgb_im.save(x+".jpg")
        x=x+".jpg"
    pictures_treated+=1
    pic=x.replace(base,"")
    filename=base+pic
    pixels = plt.imread(filename)
    # create the detector, using default weights
    detector = MTCNN()
    # detect faces in the image
    try: faces = detector.detect_faces(pixels)
    except ValueError:
        pass
    if faces != []:
        faces_num.append(len(faces))
        picture_w_faces+=1
    else:
        pictures_treated_wo_faces+=1
    draw_faces_quick(filename, faces, pic)


cropped_dir=savelocation+"/cropped/"+f"{direc}"
directo_list=list(filter(os.path.isdir, [os.path.join(cropped_dir, f) for f in os.listdir(cropped_dir)]))    

for x in directo_list:
    directory_processed+=1
    for v in os.listdir(x):    
        if ".jpg" in v:
            filepic=x+"/"+v
            ar=process_and_predict(filepic)
            gender = np.round(genmodel.predict(ar))    
        if gender == 0:
            male+=1
        elif gender == 1:
            female+=1

    summary["Site"]=direc
    summary["pictures_treated"]=pictures_treated
    summary["directory_processed"]=directory_processed
    summary["faces_num"]=sum(faces_num)
    summary["pictures_treated_wo_faces"]=pictures_treated_wo_faces
    summary["male"]=male
    summary["female"]=female
    summary["picture_w_faces"]=picture_w_faces
    if picture_w_faces !=0:
        summary["woman_gender_ratio"]=(female/picture_w_faces)/(male/picture_w_faces)
    else: 
        summary["woman_gender_ratio"]="NaN"

    if os.path.isfile(file_name):
        with open(file_name, 'a', newline='') as write_obj:
            dict_writer = DictWriter(write_obj, fieldnames=summary.keys())
            dict_writer.writerow(summary)
    else:
        with open(file_name, 'a+', newline='') as write_obj:
            dict_writer = DictWriter(write_obj, fieldnames=summary.keys())
            dict_writer.writeheader()
            dict_writer.writerow(summary) 


