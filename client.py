import sys
import re
import socket
import os

#MARK:- Global Variables
port = 0
host = ""
clientFilesDir = ""

def checkForFileDirectory():
    global clientFilesDir

    fileDir = os.path.dirname(os.path.realpath(__file__))
    clientFilesDir = os.path.join(fileDir,"ClientFiles")

#If the directory doesn't exist create a directory and create dummy files of size 2kB each
    if not os.path.exists(clientFilesDir):
        os.makedirs(clientFilesDir)
        createFile(["foo1.txt","foo2.jpg","foo3.pdf"])

def createFile(fileNames):
    for i in fileNames:
        t = os.path.join(clientFilesDir,i)
        with open(t, "wb") as out:
            out.truncate(2 * 1024 * 1024 * 1024)

#MARK:- Validation
#This function is used to validate the user input.

def isValidInput():
    try:
        validateIP(sys.argv[1])
        validatePortNumber(sys.argv[2])
    except:
        print("Kindly Enter IP Address and Port Number")
        exit()


def validateIP(ip):
    global host
    regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(
                25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''
    if (re.search(regex, ip)):
        host = ip
    else:
        print("The IP address is invalid. Please enter a valid IP address")
        exit()

def validatePortNumber(portNumber):
    global port
    try:
        port = int(portNumber)
    except ValueError:
        print("The port number you have entered is not an integer.Please enter a valid port number")
        exit()

def startClient():
    try:
       c = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print('Failed to create socket. Error:',e)
        exit()

    while(1) :
        msg = input('Please enter the command : ')
        try :
            if("put" in msg):
                commandArguments = msg.split(" ")
                if(len(commandArguments)>=2):
                    c.sendto(bytes(msg,"utf-8"),(host,port))
                    fileName = os.path.join(clientFilesDir,commandArguments[1])
                    if(doesFileExist(fileName)):
                        f = open(fileName, "rb") #→ This file is read in Binary format
                        buf = 1024
                        data = f.read(buf)
                        while (data):
                            if(c.sendto(data, (host,port))):
                                data = f.read(buf)
                        f.close()
                    else:
                        print("No such file exists.")
                else:
                    print("Please enter filename along with the command.")
            else:
                c.sendto(bytes(msg,"utf-8"),(host,port))
                if("get" in msg):
                    currentFileName = msg.split(" ")[1]
                    buf = 1024
                    data,addr = c.recvfrom(buf)
                    f = open(os.path.join(clientFilesDir,currentFileName), "wb") #→ File is written in Binary format
                    try:
                        while((data is not None)):
                            f.write(data)
                            c.settimeout(10)
                            data,addr = c.recvfrom(buf)
                            print("recv")
                    except socket.error as e:
                        f.close()
                        c.sendto(bytes("File Received","utf-8"),(host,port))
                        c.settimeout(None)
                else:
                    data, servAddr = c.recvfrom(1024)
                    print('Server reply : \n' + data.decode("utf-8"))
        except socket.error as e:
            print("Failed to send data. Error:", e)
            exit()




def doesFileExist(path):
    return os.path.exists(path)

def exit():
    print("Client Stopped")
    sys.exit(0)

if __name__ == '__main__':
    checkForFileDirectory()
    isValidInput()
    startClient()
