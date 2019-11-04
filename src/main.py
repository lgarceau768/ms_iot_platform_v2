import os, sys, socket, configparser, datetime, const
from util import rotatingLogger as logger

# Main Program
if __name__ == '__main__':
    # need to setup logging
    deviceName = socket.gethostname()
    time = datetime.datetime.now().isoformat()
    logName = '%s_msLog_%s' % (deviceName, time)
    const.LOG_NAME = logName

    # setup config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # start program
    logger.get_logger().info('Starting MS Platform')

    # need to move old log files from logs dir
    for file in os.listdir(config.get('Paths', 'logPath')):
        print(file)




