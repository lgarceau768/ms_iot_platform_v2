import os, sys, asyncio, const, socket, datetime, configparser, shutil, time
from util import rotatingLogger as logger

config = configparser.ConfigParser()

@asyncio.coroutine
async def recordData():
    # wait for program to remove other csvs
    
    while True:
        
        removes = []
        dataLarge = const.MSG_TO_RECORD
        logger.get_logger().info('---------------: '+str(len(const.MSG_TO_RECORD))+' : '+const.CAN_DATA_FILE)
        for i in range(0, len(dataLarge)):
            logger.get_logger().info('---------------------Recording data')
            logger.get_logger().info('------------: '+str(const.MSG_TO_RECORD))
            
            logger.get_logger().info('op: '+op)
            op = 'a'
            if '.csv' not in const.CAN_DATA_FILE:
                logger.get_logger().info('----------------: new csv file')
                deviceName = socket.gethostname()
                timestamp = datetime.datetime.now()
                timestamp = '%i%i%i_%i%i%s' % (timestamp.day, timestamp.month, timestamp.year, timestamp.hour, timestamp.minute, timestamp.second)
                fileName = '%s_%s.csv' % (deviceName, timestamp)
                const.CAN_DATA_FILE = fileName
                op = 'w'
            path = config.get('Paths', 'canDataPath')
            logger.get_logger().info('---------------: '+path)
            # if os.stat(os.path.join(path, const.CAN_DATA_FILE)).st_size >= int(config.get('Size', 'maxCsvSize')):
            #     logger.get_logger().info('---------------------moved csv file')
            #     try:
            #         #shutil.move(os.path.join(path, const.CAN_DATA_FILE), config.get('Paths', 'outPath'))
            #         print('lol')
            #     except Exception as e:
            #         logger.get_logger().error('Exception %s in moving %s: ' % (e, os.path.join(path, const.CAN_DATA_FILE)))
            #     deviceName = socket.gethostname()
            #     timestamp = datetime.datetime.now()
            #     timestamp = '%i%i%i_%i%i%s' % (timestamp.day, timestamp.month, timestamp.year, timestamp.hour, timestamp.minute, timestamp.second)
            #     fileName = '%s_%s.csv' % (deviceName, timestamp)
            #     const.CAN_DATA_FILE = fileName            
            logger.get_logger().info('-------------------joined name: %s' % os.path.join(path, const.CAN_DATA_FILE))
            logger.get_logger().info('--------------------data file: '+const.CAN_DATA_FILE)
            with open(os.path.join(path, const.CAN_DATA_FILE), op) as canFile:
                data = dataLarge[i]
                canTS = data[0]
                canID = data[1]
                canMG = data[2]
                formatMsg = '%s\tID: %s\tMessage: %s\n' % (canTS, canID, canMG)
                canFile.write(formatMsg)
                canFile.close()
            removes.append(data)
        for item in removes:
            const.MSG_TO_RECORD.remove(item)