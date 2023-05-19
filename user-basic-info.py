import urllib.request
import PyPDF2
import re
import csv
import tabula
import os.path as fileCheck
from os import remove as fileRem

stop = False

def getData(jsesID,servID='1684732',timeID='627120',file='data.pdf'):
    try:
        url = 'https://usis.bracu.ac.bd/academia/studentCourse/createSchedulePDF?content=pdf&studentId='+str(servID)+'&sessionId='+str(timeID)
        cookie = 'JSESSIONID='+str(jsesID)+';SRVNAME=USISA'
        opener = urllib.request.build_opener()
        opener.addheaders.append(('Cookie', cookie))
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, file)
        return True
    except KeyboardInterrupt:
        exit()
    except:
        return False

def parseData(file='data.pdf'):
    try:
        pdf_file = open(file, 'rb')
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        page = pdf_reader.pages[0]
        text = page.extract_text()
        nm = re.search("Name : .+", text).group()[7:]
        pg = re.search("Program: [A-Z]+", text).group()[9:]
        id = re.search("ID : [0-9]+", text).group()[5:]
        pdf_file.close()
        return [id,pg,nm]
    except KeyboardInterrupt:
        exit()
    except:
        return False

def parseTime(file='data.pdf'):
    try:
        times = []
        datasheet = tabula.read_pdf(file,pages=1)[0]
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
    except KeyboardInterrupt:
        exit()
    except:
        return False

def storeData(sid,id,pg,name,times,dataname='data.csv'):
    if len(times) == 0:
        tb = "NULL"
    else:
        tb = ','.join(times).strip('"')
    with open(dataname, 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([sid,id,pg,name,tb])

def getAllData(sessionID,start=1669207,steps=1,timeID=627120):
    for i in range(start,start+steps):
        if fileCheck.exists('killme'):
            fileRem('killme')
            break
        if fileCheck.exists('data.pdf'):
            fileRem('data.pdf')
        print("---------------")
        print("Getting Data",i,i-start)
        try:
            getData(sessionID,i,timeID=timeID)
            data = parseData()
            timeTable = parseTime()
            id,pg,nm = data
            storeData(i,id,pg,nm,timeTable)
            print("Data Parsed")
        except:
            print("Failed Parsing")

getAllData("E8AFD1DC58F907157E1CFBB52CFB51A0",steps=100000,start=1684732,timeID=627121)
