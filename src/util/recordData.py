import os, sys, asyncio, const, socket, datetime, configparser, shutil, time
from util import rotatingLogger as logger

config = configparser.ConfigParser()

def record(data):
    # wait for program to remove other csvs
    const.CAN_DATA_FILE = handleFile()[0]
        
    removes = []
    logger.get_logger().info('---------------: '+str(data))
    
    (fileName, opertation) = handleFile(const.CAN_DATA_FILE)
    with open(fileName, opertation) as file:
        file.write('%s,ID:\t%sMessage:\t%s' % (data[0], data[1], data[2]))
        file.close()

## need to create fucntion to handle this and then continue testing later tonight
def handleFile(file='none'):
    dataDir = config.get('Paths', 'dataPath')
    filePath = os.path.join(dataDir, file)
    operation = 'a'
    if os.path.stat(filePath).ST_SIZE >= config.get('Size', 'maxCsvSize') or file == 'none':
        os.system('mv %s /home/User1/out/%s' % (filePath, file))
        operation = 'w'
        fileName = socket.gethostname()
        fileName = fileName+'_'
        timestamp = datetime.datetime.now()
        timestamp = '%s%s%s_%s%s%s' % (timestamp.day, timestamp.month, timestamp.year, timestamp.hour, timestamp.minute, timestamp.second)
        fileName = fileName+timestamp+'.csv'
        file = fileName
    filePath = os.path.join(dataDir, file)
    return filePath, operation
