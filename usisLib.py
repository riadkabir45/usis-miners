from requests import Session as Downloader
from io import BytesIO as RawFile
from PyPDF2 import PdfReader as PdfScrap

from re import search as RegSearch
from tabula import read_pdf as PdfTableScrap

# from csv import writer as CSVWritter
# from PyPDF2 import errors as PdfTextError

# import pdb; pdb.set_trace()

class InvalidUsisUser(Exception):
    "Raised when user or pass is incorrect"
    pass
class UsisSesssionExpired(Exception):
    "Raised when user session expired"
    pass
class UsisInvalidStudent(Exception):
    "Raised when student dont exist"
    pass

def defaultRegex(patern,txt,defaultValue=None):
    out = RegSearch(patern,txt)
    if out == None:
        return defaultValue
    else:
        return out.group()

def getLocalData(oFile):
    try:
        with open(oFile) as fl:
            pre_lst = fl.read().strip("\n").split("\n")
            lst = list(map(lambda a:int(a.split(",")[0]),pre_lst))
            return lst
    except:
            return []


def getCredentials(user, passwd):
    dataDownloader = Downloader()
    dataDownloader.get("https://usis.bracu.ac.bd/academia")
    response = dataDownloader.post(
        "https://usis.bracu.ac.bd/academia/j_spring_security_check",
        data={"j_username": user, "j_password": passwd},
    )
    if (
        response.url
        == "https://usis.bracu.ac.bd/academia/login/authfail?login_error=1"
    ):
        raise InvalidUsisUser
    return dataDownloader


def getRawGrades(dataDownloader, studentID):
    checkID = 22141006
    url = (
        "https://usis.bracu.ac.bd/academia/studentGrade/"
        + "rptStudentGradeSheetByStudent?reportFormat=PDF&studentId="
        + str(checkID)
    )
    originData = dataDownloader.get(url)
    if originData.url == "https://usis.bracu.ac.bd/academia/":
        raise UsisSesssionExpired
    gradeUrl = originData.url.replace("=22141006&", "=" + str(studentID) + "&")
    rawData = dataDownloader.get(gradeUrl)
    if len(rawData.content) == 48473:
        raise InvalidUsisUser
    memFile = RawFile()
    memFile.write(rawData.content)
    return memFile


def getRawTimes(dataDownloader, serverID,sessionTime):
    url = (
        "https://usis.bracu.ac.bd/academia/studentCourse/"
        + "createSchedulePDF?content=pdf&studentId="
        + str(serverID)
        + "&sessionId="+str(sessionTime)
    )
    rawData = dataDownloader.get(url)
    if rawData.url == "https://usis.bracu.ac.bd/academia/":
        raise UsisSesssionExpired
    if rawData.status_code == 500:
        raise UsisInvalidStudent
    memFile = RawFile()
    memFile.write(rawData.content)
    return memFile


def parseTimes(tFile):
    text = PdfScrap(tFile).pages[0].extract_text()
    nm = defaultRegex("Name : .+", text,"xxxxxxxNULL")[7:]
    pg = defaultRegex("Program: [A-Z]+", text,"xxxxxxxxxNULL")[9:]
    uid = defaultRegex("ID : [0-9]+", text,"xxxxxNULL")[5:]

    times = [nm, pg, uid]

    datasheet = PdfTableScrap(tFile, pages=1, silent=True)[0]
    for index in datasheet:
        if index == "Time/Day":
            continue
        for i in range(len(datasheet[index])):
            data = str(datasheet[index][i])
            if data == "nan":
                continue
            data = data.replace("\r", " ")
            time = str(datasheet["Time/Day"][i]).replace("\r", "")
            times.append(index[:3] + "(" + time + " - " + data + ")")
    return times

def getSingleAdvising(dataDownloader,serverID,sessionTime,storeFile=None):
    print("\nI: Processing", serverID)
    rawFile = getRawTimes(dataDownloader,serverID, sessionTime)
    print("I: Parsing Info and Time")
    timeTable = parseTimes(rawFile)
    print("I: Storing Data")
    print("I: Processing Done")
    if len(timeTable) == 3:
        timeTable.append("NULL")
    if type(storeFile) == str:
        oFile = open(storeFile,"a")
        if db:
            dpush(timeTable[2],serverID,timeTable[0],timeTable[1])
        print(f"{serverID},{','.join(timeTable[2::-1])},{','.join(timeTable[3:])}",file=oFile)
        oFile.close()

