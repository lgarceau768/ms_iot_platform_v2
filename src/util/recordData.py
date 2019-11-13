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
           print(str(dataLarge[i]))
           removes.append(data)
        for item in removes:
            const.MSG_TO_RECORD.remove(item)