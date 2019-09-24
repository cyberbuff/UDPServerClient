import sys
import socket
import os

port = 0
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
c = ""
prevCommand = ""
currentFileName = ""
serverFilesDir = ""


def checkForFileDirectory():
    global serverFilesDir

    fileDir = os.path.dirname(os.path.realpath(__file__))
    serverFilesDir = os.path.join(fileDir,"ServerFiles")

    if not os.path.exists(serverFilesDir):
        os.makedirs(serverFilesDir)

#MARK :- Validation
# This function is used to check whether the user input is valid

def startValidation():
    try:
        validatePortNumber(sys.argv[1])
    except:
        print("Kindly enter the port number")
        exit()


def validatePortNumber(portNumber):
    global port
    try:
        port = int(portNumber)
    except ValueError:
        print("The port number you have entered is not an integer.Kindly enter a valid port number")
        exit()

# MARK :- Server Initialization
def startServer():
    s.bind(("", port))
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    print("Server started on ", ip_address, ":", port)
    handleInputForSocket(s)


def handleInputForSocket(s):
    global c
    while 1:
        try:
            if(prevCommand == "put"):
                receiveFile()
            else:
                encodedCommandFromClient, clientAddr = s.recvfrom(1024)
                c = clientAddr
                commandFromClient = encodedCommandFromClient.decode("utf-8")
                handleClientCommand(commandFromClient)
        except Exception as e:
            print('Error while sending/receiving message',e)
            if(e != "timed out"):
                print(e)
            # if(e != socket.timeout):
                # exit()


def handleClientCommand(command):
    global prevCommand,currentFileName
    commandArguments = command.split(" ")

    function = commandArguments[0]
    prevCommand = function
    if function == "list":
        listFiles()
    elif function == "exit":
        sendMessage("Server Stopped.")
        exit()
    elif function == "get":
        if(len(commandArguments) > 1):
            currentFileName = commandArguments[1]
            getFile(currentFileName)
        else:
            sendMessage("Please Enter Filename")
    elif function == "put":
        currentFileName = commandArguments[1]
    elif function == "rename":
        if(len(commandArguments) > 2):
            renameFile(commandArguments[1], commandArguments[2])
        else:
            sendMessage("Invalid Command. Error: ")
    else:
        sendMessage("""
Please enter a valid command
get [file_name]
put [file_name]
rename [old_file_name] [new_file_name]
list
exit
                    """)


def sendMessage(message):
    s.sendto(bytes(message, "utf-8"), c)

def doesFileExist(path):
    return os.path.exists(path)

def listFiles():
    files = "Files in the Directory :\n"
    files += "\n".join(os.listdir(serverFilesDir))
    sendMessage(files)

def renameFile(oldFileName, newFileName):
    oldFile = os.path.join(serverFilesDir,oldFileName)
    if(doesFileExist(oldFile)):
        os.rename(os.path.join(serverFilesDir,oldFileName),os.path.join(serverFilesDir,newFileName))
        sendMessage("The file has been renamed to "+newFileName)
    else:
        sendMessage("No such file exists. Check the list command to show the files in the current directory.")

def getFile(fileName):
    print("tet")
    file = os.path.join(serverFilesDir,fileName)
    if(doesFileExist(file)):
        f = open(file, "rb") #→ This file is read in Binary format
        buf = 1024
        data = f.read(buf)
        while (data):
            if(s.sendto(data, c)):
                data = f.read(buf)
                print("send")
        f.close()
    else:
        sendMessage("No such file exists.")

def receiveFile():
    global prevCommand
    prevCommand = ""
    buf = 1024
    data,addr = s.recvfrom(buf)
    f = open(os.path.join(serverFilesDir,currentFileName), "wb") #→ File is written in Binary format

    try:
        while((data is not None)):
            f.write(data)
            s.settimeout(10)
            data,addr = s.recvfrom(buf)
    except socket.error as e:
        f.close()
        sendMessage("File Received")
        s.settimeout(None)

def exit():
    print("Server Stopped")
    sys.exit(0)

if __name__ == '__main__':
    checkForFileDirectory()
    startValidation()
    startServer()
