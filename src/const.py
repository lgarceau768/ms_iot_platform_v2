import os

# global variables
CONFIG_PATH = '/home/User1/msV2/src/config.ini'
LOG_NAME = ''
CAN_DATA_FILE = 'none'
CAN_CODES_FILE = '/home/User1/msV2/data/canCodes.txt'
SERVICE_FILE = '/home/User1/msV2/data/'

# shared data amongst the threads
CAN_DATA = []
CAN_CODES = []
MSG_TO_SEND = []
MSG_TO_RECORD = []
SERVICE_DATA = []

# iot variables
DEVICE_TWIN = None
IOT_CLIENT = None