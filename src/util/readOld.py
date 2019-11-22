import os, const as const
from util import rotatingLogger as logger


def readOldCanData():
    while True:
        list = []
        with open(const.CAN_CODES_FILE, 'r') as codes:
            lines = codes.readlines()
            for line in lines:
                logger.get_logger().info('READING CAN CODES: '+str(line))
                list.append(lines.strip().split(' '))
        const.CAN_CODES = list

def recordCanData():
    while True:
        with open(const.CAN_CODES_FILE, 'w') as codes:
            for el in const.CAN_CODES:
                line = el[0]+' '+el[1]+' '+el[2]
                codes.write(line+'\n')
            codes.close() 