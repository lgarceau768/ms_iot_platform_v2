import os, sys, socket, configparser, datetime, const, shutil
from util import rotatingLogger as logger

# Main Program
if __name__ == '__main__':
    # setup config file
    config = configparser.ConfigParser()
    config.read('config.ini')

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




