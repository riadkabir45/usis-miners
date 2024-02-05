from usisLib import *
from sys import argv

absent_threshold = 5000
starting_id = 1662369
id_range = 40000
session_time = 627123
out_file = "data.csv"

user = ""
passwd = ""

if len(argv) >= 3:
    user = argv[1]
    passwd = argv[2]

if len(argv) >= 4:
    starting_id = int(argv[3])

if len(argv) >= 5:
    id_range = int(argv[4])

def getBatchAdvising(dataDownloader,startID=1669207, time=627120,oFile="data.csv"):
    absent_error = 0
    serverID = startID
    lasID = serverID
    while True:
        try:
            if absent_threshold > 0 and absent_error > absent_threshold:
                print("E: Range thresold crossed from",lastID)
                break
                
            getSingleAdvising(dataDownloader,serverID,time,oFile)
            absent_error = 0
            lastID = serverID
            serverID -= 1000
            
        except UsisInvalidStudent:
            absent_error += 1
            print("W: Student not found at threshold -",absent_error)
            serverID -= 1
        except UsisSesssionExpired:
            curl = getCredentials(user,passwd)
               

try:
    curl = getCredentials(user,passwd)
    getBatchAdvising(curl,starting_id,session_time,out_file)
except InvalidUsisUser:
    print("E: User or pass is incorrect")


