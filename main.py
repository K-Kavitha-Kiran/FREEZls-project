import cv2
import csv
# import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def sendmail(text, html, data, subject, header):

    me = 'freezls.project@gmail.com'
    password = "MiniProject"
    #transport layer security port number
    server = 'smtp.gmail.com:587'
    #you = input()
    you = 'kavitha.kasivajjhala@gmail.com'

    text = text.format(table=tabulate(data, headers=header, tablefmt="grid"))
    html = html.format(table=tabulate(data, headers=header, tablefmt="html"))

    message = MIMEMultipart(
        "alternative", None, [MIMEText(text), MIMEText(html,'html')])

    message['Subject'] = subject
    message['From'] = me
    message['To'] = you
    #main statement
    server = smtplib.SMTP(server)
    server.ehlo()
    server.starttls()
    server.login(me, password)
    server.sendmail(me, you, message.as_string())
    server.quit()

def alert():
    text = """
    Hello, User.
    Here is the list of Items about to expire:
    {table}
    Regards,
    Smart Fridge"""

    html = """
    <html><body><p>Hello, User.</p>
    <p>Here is the list of Items about to expire:</p>
    {table}
    <p>Regards,</p>
    <p>Smart Fridge</p>
    </body></html>
    """

    with open('items_list.csv') as input_file:
        reader = csv.reader(input_file)
        ldata = list(reader)
    #alert prior to expiry
    alertdays=3
    #sorting in order of expiry
    ldata=(sorted(ldata, key = lambda x: x[2]))
    data=[]
    for i in range(len(ldata)):
        datestr = (datetime.strptime(ldata[i][2][:10], "%Y-%m-%d"))
        if((datestr.date() - date.today()).days > alertdays):
            break
        data.append([ldata[i][0],ldata[i][2]])

    if(len(data)>=1):
        subject= "Alert!! Items about to Expire"
        header = ["Item Name","Date of Expiry"]
        sendmail(text, html, data, subject, header)
        print("=>  Alert Sent  <=")
        #prevdate=date.today()
    else:
        print("Your Fridge is Fresh!")

#dictionary to store Category, Best Before.
items = {}
items["banana"] = ["Fruit", 5]
items["apple"] = ["Fruit", 9]
items["carrot"] = ["Vegetable", 11]
items["orange"] = ["Fruit", 14]
items["broccoli"] = ["Vegetable", 4]
items["tomato"] = ["Vegetable", 3]
items["bottle"] = ["Other", 5]
items["sandwich"] = ["Snacks", 3]
items["hot dog"] = ["Snacks", 7]
items["pizza"] = ["Snacks", 3]
items["donut"] = ["Snacks", 6]
items["cake"] = ["Snacks", 3]

def listMail():
    text = """
    Hello, User.
    Here is your data:
    {table}
    Regards,
    Smart Fridge"""

    html = """
    <html><body><p>Hello, User.</p>
    <p>Here is your data:</p>
    {table}
    <p>Regards,</p>
    <p>Smart Fridge</p>
    </body></html>
    """

    with open('items_list.csv') as input_file:
        reader = csv.reader(input_file)
        data = list(reader)
    header = ["Name", "Date of Insertion", "Expiry Date", "Category"]
    subject = "Here is your data"
    sendmail(text, html, data, subject, header)
    print("=>  List Mailed  <=")
   
def recognition():
    thres = 0.70 # Threshold to detect object

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # cap.set(3,1280)
    # cap.set(4,720)
    # cap.set(10,70)
    # print(cap)
    classNames= []
    classFile = 'coco.names'
    with open(classFile,'rt') as f:
        classNames = f.read().rstrip(' ').split('\n')
    # print(classNames)
    configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    weightsPath = 'frozen_inference_graph.pb'

    net = cv2.dnn_DetectionModel(weightsPath,configPath)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    if(True):
        i = 1
        flag = False
        while(True):
            success,img = cap.read()
            # cv2.imshow('',img)
            classIds, confs, bbox = net.detect(img,confThreshold=thres)
                # print(classIds,bbox)

            if len(classIds) != 0:
                for classId, confidence,box in zip(classIds.flatten(),confs.flatten(),bbox):
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    # cv2.putText(img,classNames[classId-1],(box[0]+10,box[1]+30),
                    # cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    # cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),
                    # cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    if(classNames[classId-1] in items):
                        return classNames[classId-1]
            cv2.imshow('Output',img)
            cv2.waitKey(1)

def insert():
    #recognition
    Item_name = recognition()
    print("added",Item_name,"list updated")
    with open('items_list.csv', mode='a',newline='') as items_list:
        #to avoid extra line gaps
        items_writer = csv.writer(items_list, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        dateTimeObj = datetime.now()
        day = str(str(dateTimeObj.day)+"-"+str(dateTimeObj.month)+"-"+str(dateTimeObj.year)+" "+str(dateTimeObj.hour)+":"+str(dateTimeObj.minute))
        # date = datetime.datetime().strftime(today,"%d-%m-%Y, %H:%M")
        expiry = date.today() + timedelta(days=items[Item_name][1])
        # row of csv file   ( item name ,insert datetime, expiry, Category)
        items_writer.writerow([Item_name, day, expiry, items[Item_name][0]])
            
def delete():
    #store csv file data into list
    Item_name = recognition()
    with open('items_list.csv') as input_file:
        reader = csv.reader(input_file)
        data = list(reader)
        
        for idx in range(len(data)):
            if(data[idx][0]==Item_name):
                print("deleted",data[idx][0],"inserted on",data[idx][1])
                data.remove(data[idx])
                break 
        #reopen csv file and write changes
        with open('items_list.csv', 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(data)

#prevdate="22-06-2021"
#if(prevdate!=date.today()): or   #if(time==give_time()):
    #alert()
#input from user
k = input("Enter your choice\n \ti to insert\tl for list\ta for alert\td to delete\n")
if(k=='i'):
    while(k=='i'):
        insert()
        k = input("Enter your choice\n\ti to insert\ts to stop\n")
elif(k=='l'):
    listMail()
elif(k=='d'):
    delete()
elif(k=='a'):
    alert()
else:
    print("NO OPTION, Run again")