import os, sys, can, asyncio, traceback, configparser, const, time, math
from util import rotatingLogger as logger

# setup config file
config = configparser.ConfigParser()
config.read(const.CONFIG_PATH)

# convert epoch to datetime
def epoch_to_datetime(epoch):
    seconds_milliseconds = math.modf(epoch)
    milliseconds = seconds_milliseconds[0] * 1000.0
    seconds = seconds_milliseconds[1]
    # mm/dd/yyyy hh:mm:ss:zzz
    return "{}:{:03d}".format(time.strftime("%m/%d/%Y %H:%M:%S", time.gmtime(int(seconds))), int(milliseconds))

# convert array to hex
def hexify_array(hex_array):
        return " ".join("{:02x}".format(x) for x in hex_array)

# convert number to hex
def hexify_int(number):
        return "".join("0x{:02x}".format(number))

@asyncio.coroutine
async def readData():
    # will append data to const.CAN_DATA
    try:
        can_bus = can.interface.Bus(bustype='socketcan', channel='can0', bitrate=500000)
    except Exception as e:
        error = traceback.format_exc()
        logger.get_logger().error(error)
        logger.get_logger().error(str(e))
    
    logger.get_logger().info('Created CAN Bus')
    filters = config.get('Can', 'filters').strip().lower().split(',')
    print(str(filters))
    while True:
        #print('reading')
        try:
            message = can_bus.recv()
            if message is not None:
                canID = hexify_int(message.arbitration_id)
                if canID.lower() not in filters:
                    canMessage = hexify_array(message.data)
                    timestamp = epoch_to_datetime(message.timestamp)
                    message = '%s ID: %s Message: %s' % (str(timestamp), str(canID), str(canMessage))
                    messageObj = (timestamp, canID, canMessage)
                    const.CAN_DATA.append(messageObj)
                    #print(str(const.CAN_DATA))
        except Exception as e:
            error = traceback.format_exc()
            logger.get_logger().error(error)
            logger.get_logger().error(str(e))  
        
