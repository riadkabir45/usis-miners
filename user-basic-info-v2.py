from requests import Session as Downloader
from io import BytesIO as RawFile
from PyPDF2 import PdfReader as PdfScrap
from re import search as RegSearch
from tabula import read_pdf as PdfTableScrap
from csv import writer as CSVWritter
from PyPDF2 import errors as PdfTextError

def getRawData(sessionId,serverID="USISB",studentID=1684732,time=627120):
    url = 'https://usis.bracu.ac.bd/academia/studentCourse/createSchedulePDF?\
        content=pdf&studentId='+str(studentID)+'&sessionId='+str(time)
    dataDownloader = Downloader()
    dataDownloader.cookies.set("JSESSIONID",sessionId)
    dataDownloader.cookies.set("SRVNAME",serverID)
    rawData = dataDownloader.get(url)
    memFile = RawFile()
    memFile.write(rawData.content)
    return memFile

def parseData(file):
    text = PdfScrap(file).pages[0].extract_text()
    nm = RegSearch("Name : .+", text).group()[7:]
    pg = RegSearch("Program: [A-Z]+", text).group()[9:]
    id = RegSearch("ID : [0-9]+", text).group()[5:]
    return [id,pg,nm]

def parseTime(file):
    times = []
    datasheet = PdfTableScrap(file,pages=1)[0]
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

def storeData(sid,id,pg,name,times,dataname='data.csv'):
    if len(times) == 0:
        tb = "NULL"
    else:
        tb = ''.join(times)
    with open(dataname, 'a') as csvfile:
        csvwriter = CSVWritter(csvfile)
        csvwriter.writerow([sid,id,pg,name,tb])

def getBatchData(sessionId,serverID="USISB",startID=1669207,steps=-10,time=627120):
    errors = 0
    total = steps
    while True:
        if steps != -10:
            steps -= 1
        elif steps < 0:
            break
        id = startID+(total-steps)
        try:
            print("\nI: Processing",id)
            rawFile = getRawData(sessionId,serverID,id,time)
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
                rawFile = getRawData(sessionId,serverID,1684732,627120)
                id,pg,nm = parseData(rawFile)
            except PdfTextError.PdfReadError:
                print("E: Session Key Expired!!")
                exit()
            print("W: Data Missing!!")
            errors += 1
            if errors >= 10:
                print("E: Range Expired!!")
                exit()
        except Exception as error:
            print(f"E: Failed Parsing!!({type(error)}:{error})")
            exit()
    print("\nI: Batch Complete")

getBatchData("01295164D4D82E5D0C3290BCC6168E04",startID=1669207,steps=10)
