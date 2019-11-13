import os, sys, asyncio, const, socket, datetime, configparser, shutil, time
from util import rotatingLogger as logger

config = configparser.ConfigParser()

@asyncio.coroutine
async def recordData():
    # wait for program to remove other csvs
    
    while True:
        logger.get_logger().info('Recording data')
        removes = []
        for i in range(len(const.MSG_TO_RECORD)):
            data = const.MSG_TO_RECORD[i]
            if const.CAN_DATA_FILE == '':
                deviceName = socket.gethostname()
                timestamp = datetime.datetime.now()
                timestamp = '%i%i%i_%i%i%s' % (timestamp.day, timestamp.month, timestamp.year, timestamp.hour, timestamp.minute, timestamp.second)
                fileName = '%s_%s.csv' % (deviceName, timestamp)
                const.CAN_DATA_FILE = fileName
            path = config.get('Paths', 'canDataPath')
            if os.stat(os.path.join(path, const.CAN_DATA_FILE)).st_size >= int(config.get('Size', 'maxCsvSize')):
                try:
                    shutil.move(os.path.join(path, const.CAN_DATA_FILE), config.get('Paths', 'outPath'))
                except Exception as e:
                    logger.get_logger().error('Exception %s in moving %s: ' % (e, os.path.join(path, const.CAN_DATA_FILE)))
                deviceName = socket.gethostname()
                timestamp = datetime.datetime.now()
                timestamp = '%i%i%i_%i%i%s' % (timestamp.day, timestamp.month, timestamp.year, timestamp.hour, timestamp.minute, timestamp.second)
                fileName = '%s_%s.csv' % (deviceName, timestamp)
                const.CAN_DATA_FILE = fileName            

            with open(os.path.join(path, const.CAN_DATA_FILE), 'a') as canFile:
                canTS = data[0]
                canID = data[1]
                canMG = data[2]
                formatMsg = '%s\tID: %s\tMessage: %s\n' % (canTS, canID, canMG)
                canFile.write(formatMsg)
                canFile.close()
            removes.append(data)
        for item in removes:
            const.MSG_TO_RECORD.remove(item)