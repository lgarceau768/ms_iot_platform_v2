import os, sys, configparser, const, traceback
from util import rotatingLogger as logger

config = configparser.ConfigParser()
config.read(const.CONFIG_PATH)

def getHygieneInfo():
    # hygiene data to text file like this:
    # startTime|endTime|type
    with open(config.get('Paths', 'hygieneData'), 'r') as hygFile:
        lines = hygFile.readlines()
        info = lines[0]
        try:
            split = info.strip().split('|')
            if len(split) == 3:
                return split
            else:
                logger.get_logger().error('Hygiene data: %s invalid format' % info)
        except Exception as e:
            error = traceback.format_exc()
            logger.get_logger().error(error)
            logger.get_logger().error(str(e))
        hygFile.close()
    logger.get_logger().error('getHygieneInfo should not reach here')

def setHygieneInfo(start, stop, typeHyg):
    with open(config.get('Paths', 'hygieneData'), 'w') as hygFile:
        hygFile.write('%s|%s|%s\n' % (start, stop, typeHyg))
        hygFile.close()