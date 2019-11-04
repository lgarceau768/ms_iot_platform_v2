import os, sys, socket, configparser, datetime, const, shutil, asyncio
from util import readCan, rotatingLogger as logger, hexToEng

@asyncio.coroutine
async def msIot():
    # need to connect to iotc and read can data
    await asyncio.gather(readCan.readData(), hexToEng.interpret())

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
    logger.setup_logger(const.LOG_NAME, config.get('Paths', 'logPath'))


    # start program
    logger.get_logger().info('Starting MS Platform')

    # need to move old log files from logs dir
    for file in os.listdir(config.get('Paths', 'logPath')):
        if file.endswith('.log'):
            shutil.move(os.path.join(config.get('Paths', 'logPath'), file), config.get('Paths', 'outPath'))

    # need to move old csv files from csv dir
    for file in os.listdir(config.get('Paths', 'dataPath')):
        if file.endswith('.csv'):
            shutil.move(os.path.join(config.get('Paths', 'logPath'), file), config.get('Paths', 'outPath'))

    asyncio.run(msIot())


