import os, csv, sys, socket, datetime
import const as const
import configparser
from util import rotatingLogger as logger

config = configparser.ConfigParser()
config.read(const.CONFIG_PATH)

def recordToCSV():
    fileName = getFileName()
    servicePath = os.path.join(const.SERVICE_FILE, getFileName().replace('.csv', 'serviceData.csv'))
    path = os.path.join(config.get('Paths', 'dataPath'), fileName)
    logger.get_logger().info('Service Data Path %s' % servicePath)
    logger.get_logger().info('CSV Filename: %s Path: %s' % (fileName, path))
    while True:
        #logger.get_logger().info('recording codes')
        #with open(const.CAN_CODES_FILE, 'w') as codes:
        #    for el in const.CAN_CODES:
        #        line = el[0]+' '+el[1]+' '+el[2]
        #        codes.write(line+'\n')
        #    codes.close() 
        usingServicePatch = False
        if usingServicePatch:
        ### Writing Service Data
            serviceOperation = 'w'
            if os.path.isfile(servicePath):
                serviceOperation = 'a'

            serviceRemove1 = []
            serviceRemove2 = []
            with open(servicePath, serviceOperation) as sFile:
                for item in const.SERVICE_DATA:
                    if item not in serviceRemove1 and item not in serviceRemove2:
                        if item is tuple:
                            sFile.write(writeMsg(item))
                            serviceRemove2.append(item)
                        else:
                            timestamp = datetime.datetime.today().isoformat()
                            sFile.write(timestamp+'\t'+item+'\n')
                            serviceRemove1.append(item)
        
        for item in serviceRemove1:
            const.SERVICE_DATA.remove(item)
        for item in serviceRemove2:
            const.SERVICE_DATA.remove(item)

        ### Writing CAN Data

        operation = 'w'
        (fileName, path) = needMove(fileName, path)
        #logger.get_logger().info('===========After needMove: %s %s' % (fileName, path))
        if os.path.isfile(path):
            operation = 'a'
        remove = []
        with open(path, operation) as csvFile:
            #logger.get_logger().info('here')
            for data in const.MSG_TO_RECORD:                
                if data not in remove:
                    #logger.get_logger().info('===== size: %s' % str(len(const.MSG_TO_RECORD)))
                    remove.append(data)
                   # logger.get_logger().info('====== data: %s' % str(data))
                    csvFile.write(writeMsg(data))

            csvFile.close()
        for item in remove:
            const.MSG_TO_RECORD.remove(item)


def writeMsg(data):
    canTS = data[0]
    canID = data[1]
    canMSG = data[2]
    msg = '%s,ID: %s Message: %s\n' % (canTS, canID, canMSG)
    logger.get_logger().info('=====msg: %s' % msg)
    return msg

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
    return fileName+month+day+year+'_'+hour+minute+second+'.csv'

def needMove(fileName, path):
    maxSize = config.get('Size', 'maxCsvSize')
    outpath = config.get('Paths', 'outPath')
    outpath = os.path.join(outpath, fileName)
    #logger.get_logger().info('======max size: %s' % maxSize)
    if os.path.isfile(path):
        #logger.get_logger().info('=========getsize %s' % os.path.getsize(path))
        if os.path.getsize(path) >= int(maxSize):
            os.system('mv %s %s' % (path, outpath))
            newName = getFileName()
            path = os.path.join(config.get('Paths', 'dataPath'), fileName)
            logger.get_logger().info('Moved file %s new file %s' % (fileName, newName))
            return (newName, path)
        else:
            return (fileName, path)
    else:
        return (fileName, path)