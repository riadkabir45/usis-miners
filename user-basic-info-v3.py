from usisLib import *
from sys import argv

absent_threshold = 250
starting_id = 1662369
id_range = 40000
session_time = 627123
out_file = "data.csv"

user = ""
passwd = ""

if len(argv) == 3:
    out_file = f"dataN{argv[1]}.csv"
    starting_id = int(argv[2])

def getBatchAdvising(dataDownloader,startID=1669207, steps=10, time=627120,oFile="data.csv"):
    absent_error = 0
    oLst = getLocalData(oFile)
    for serverId in range(startID,startID+steps):
        try:
            if absent_threshold > 0 and absent_error > absent_threshold:
                print("E: Range thresold crossed")
                break
                
            if serverId in oLst:
                continue
            getSingleAdvising(dataDownloader,serverId,time,oFile)
            absent_error = 0
            
            
        except UsisInvalidStudent:
            absent_error += 1
            print("W: Student not found")
        except UsisSesssionExpired:
            curl = getCredentials(user,passwd)
               

try:
    curl = getCredentials(user,passwd)
    getBatchAdvising(curl,starting_id,id_range,session_time,out_file)
except InvalidUsisUser:
    print("E: User or pass is incorrect")


