from requests import Session as Downloader
from io import BytesIO as RawFile
from PyPDF2 import PdfReader as PdfScrap
from re import search as RegSearch
from tabula import read_pdf as PdfTableScrap
from csv import writer as CSVWritter
from PyPDF2 import errors as PdfTextError
import sys

if len(sys.argv) == 3:
    username = sys.argv[1]
    password = sys.argv[2]
else:
    username = input("Usis Username: ")
    password = input("Usis Password: ")

error_thresold = 100
outpit = "data.csv"
dataDownloader = Downloader()

def getRawData(studentID=1684732,time=627120):
    url = 'https://usis.bracu.ac.bd/academia/studentCourse/createSchedulePDF?\
        content=pdf&studentId='+str(studentID)+'&sessionId='+str(time)
    rawData = dataDownloader.get(url)
    memFile = RawFile()
    memFile.write(rawData.content)
    return memFile

def parseData(file):
    text = PdfScrap(file).pages[0].extract_text()
    nm = RegSearch("Name : .+", text).group()[7:]
    pg = RegSearch("Program: [A-Z]+", text).group()[9:]
    uid = RegSearch("ID : [0-9]+", text).group()[5:]
    return [uid,pg,nm]

def parseTime(file):
    times = []
    datasheet = PdfTableScrap(file,pages=1,silent=True)[0]
    for index in datasheet:
        if index == 'Time/Day':
            continue
        for i in range(len(datasheet[index])):
            data = str(datasheet[index][i])
            if data == 'nan':
                continue
            data = data.replace('\r',' ')
            time = str(datasheet['Time/Day'][i]).replace('\r','')
            times.append(index[:3]+"("+time+" - "+data+")")
    return times

def storeData(sid,uid,pg,name,times,dataname=outpit):
    if len(times) == 0:
        tb = "NULL"
    else:
        tb = ''.join(times)
    with open(dataname, 'a') as csvfile:
        csvwriter = CSVWritter(csvfile)
        csvwriter.writerow([sid,uid,pg,name,tb])

def getCredentials(user,passwd):
	dataDownloader.get("https://usis.bracu.ac.bd/academia")
	dataDownloader.post("https://usis.bracu.ac.bd/academia/j_spring_security_check",data={"j_username": user,"j_password": passwd})

def getBatchData(startID=1669207,steps=-10,time=627120):
    getCredentials(username,password)
    errors = 0
    total = steps
    while True:
        if steps != -10:
            steps -= 1
        elif steps < 0:
            break
        uid = startID+(total-steps)
        try:
            print("\nI: Processing",uid)
            rawFile = getRawData(uid,time)
            print("I: Parsing Info")
            id,pg,nm = parseData(rawFile)
            print("I: Parsing Time")
            timeTable = parseTime(rawFile)
            print("I: Storing Data")
            storeData(id,id,pg,nm,timeTable)
            print("I: Processing Done")
            errors = 0
        except KeyboardInterrupt:
            exit()
        except PdfTextError.PdfReadError:
            try:
                rawFile = getRawData(1684732,627120)
                id,pg,nm = parseData(rawFile)
            except PdfTextError.PdfReadError:
                print("E: Wrong Session Keys!!")
                exit()
            print("W: Data Missing!!")
            errors += 1
            if errors >= error_thresold:
                print("E: Range Expired!!")
                exit()
        except Exception as error:
            print(f"E: Failed Parsing!!({type(error)}:{error})")
            exit()
    print("\nI: Batch Complete")

getBatchData(startID=1669207,steps=5)
