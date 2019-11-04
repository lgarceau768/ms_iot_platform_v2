import os, sys, socket, configparser, datetime, const, shutil, asyncio
from util import readCan, rotatingLogger as logger, hexToEng
from threading import Thread

@asyncio.coroutine
async def msIot():
    # need to connect to iotc and read can data
    print('gather')
    t1 = Thread(target=readCan.readData)
    t2 = Thread(target=hexToEng.interpret)
    await t1.start()
    await t2.start()

    

# Main Program
if __name__ == '__main__':
    # setup config file
    config = configparser.ConfigParser()
    config.read(const.CONFIG_PATH)

    # need to setup logging
    deviceName = socket.gethostname()
    time = datetime.datetime.now().isoformat()
    logName = '%s_msLog_%s' % (deviceName, time)
    const.LOG_NAME = logName
    logger.setup_logger(const.LOG_NAME, '/home/User1/msV2/logs/')


    # start program
    logger.get_logger().info('Starting MS Platform')

    # need to move old log files from logs dir
    for file in os.listdir(config.get('Paths', 'logPath')):
        if file.endswith('.log') and logName not in file:
            shutil.move(os.path.join(config.get('Paths', 'logPath'), file), config.get('Paths', 'outPath'))

    # need to move old csv files from csv dir
    for file in os.listdir(config.get('Paths', 'dataPath')):
        if file.endswith('.csv'):
            shutil.move(os.path.join(config.get('Paths', 'logPath'), file), config.get('Paths', 'outPath'))

    asyncio.run(msIot())


