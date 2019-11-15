import os, sys, socket, configparser, datetime, const, shutil, asyncio
from util import readCan, rotatingLogger as logger, hexToEng, recordData, sendIotc
from threading import Thread

@asyncio.coroutine
async def msIot():
    # need to connect to iotc and read can data
    client = await sendIotc.connect()

    # using a 5 threaded parrellism system
    read = Thread(target=runRead)
    translate = Thread(target=runTranslate)
    record = Thread(target=runRecord)
    update = Thread(target=runUpdate, args=[client])
    send = Thread(target=runSend, args=[client])

    # all threads run in parallel and have shared mutex data
    read.start()
    translate.start()
    #record.start()
    #update.start()
    send.start()

def runRead():
    asyncio.run(readCan.readData())

def runTranslate():
    asyncio.run(hexToEng.interpret())
    
def runRecord():
    asyncio.run(recordData.recordData())

def runSend(client):
    asyncio.run(sendIotc.sendMessages(client))

def runUpdate(client):
    asyncio.run(sendIotc.settingsChange(client))

# Main Program
if __name__ == '__main__':
    # setup config file
    config = configparser.ConfigParser()
    config.read(const.CONFIG_PATH)

    # need to setup logging
    deviceName = socket.gethostname()
    time = datetime.datetime.now().isoformat()
    logName = '%s_msLog_%s' % (deviceName, time)
    path = os.path.join('/home/User1/msV2/logs', logName)
    const.LOG_NAME = logName
    logger.setup_logger(path, '/home/User1/msV2/logs/')


    # start program
    logger.get_logger().info('Starting MS Platform')

    # need to move old log files from logs dir
    for file in os.listdir(config.get('Paths', 'logPath')):
        if file.endswith('.log') and logName not in file:
            filePathCurr = os.path.join(config.get('Paths', 'logPath'), file)
            dest = os.path.join(config.get('Paths', 'outPath'), file)
            try:
                os.system('mv %s %s' % (filePathCurr, dest))
            except Exception as e:
                logger.get_logger().info('Exception %s in moving %s' % (filePathCurr, dest))

    # need to move old csv files from csv dir
    for file in os.listdir(config.get('Paths', 'dataPath')):
        if file.endswith('.csv'):
            filePathCurr = os.path.join(config.get('Paths', 'dataPath'), file)
            dest = os.path.join(config.get('Paths', 'outPath'), file)
            try:
                os.system('mv %s %s' % (filePathCurr, dest))
            except Exception as e:
                logger.get_logger().info('Exception %s in moving %s' % (filePathCurr, dest))

    asyncio.run(msIot())


