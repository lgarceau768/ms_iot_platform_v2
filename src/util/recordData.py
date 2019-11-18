import os, csv, sys, socket, datetime
import const as const
import configparser
from util.rotatingLogger import logger

config = configparser.ConfigParser()
config.read(const.CONFIG_PATH)

def recordToCSV():
    fileName = getFileName()
    logger.info('Filename: %s' % fileName)
    path = os.path.join(config.get('Paths', 'dataPath'), fileName)
    while True:
        operation = 'w'
        (fileName, path) = needMove(fileName, path)
        if os.path.isfile(path):
            operation = 'a'
        remove = []
        with open(fileName, operation) as csvFile:
            for data in const.MSG_TO_RECORD:
                remove.append(data)
                writeMsg(csvFile, data)
            csvFile.close()
        for item in remove:
            const.MSG_TO_RECORD.remove(item)
        

def writeMsg(file, data):
    canTS = data[0]
    canID = data[1]
    canMSG = data[2]
    msg = '%s,ID: %s Message: %s\n' % (canTS, canID, canMSG)
    file.write(msg)

def getFileName():
    fileName = socket.gethostname()
    fileName = fileName+'_'
    today = datetime.datetime.now()
    day = str(today.day)
    month = str(today.month)
    year = str(today.year)
    hour = str(today.hour)
    minute = str(today.minute)
    second = str(today.second)
    return fileName+day+month+year+'_'+hour+minute+second+'.csv'

def needMove(fileName, path):
    maxSize = config.get('Size', 'maxCsvSize')
    outpath = config.get('Paths', 'outPath')
    outpath = os.path.join(outpath, fileName)
    if os.stat(path).st_size >= int(maxSize):
        os.system('mv %s %s' % (path, outpath))
        newName = getFileName()
        path = os.path.join(config.get('Paths', 'dataPath'), fileName)
        logger.info('Moved file %s new file %s' % (fileName, newName))
        return (newName, path)
    else:
        return (fileName, path)
