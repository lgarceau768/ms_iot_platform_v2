import datetime
import logging
import os
import shutil
import inspect
import socket
import datetime
from logging.handlers import RotatingFileHandler


logger = None
logWhat = []

class ExportedRotatingFileHandler(RotatingFileHandler):
    destination_dir = None

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d" % (self.baseFilename, i)
                dfn = "%s.%d" % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            shutil.move(self.baseFilename, self.destination_dir)
            if os.path.exists(dfn):
                os.remove(dfn)
        # Generate a new timestamped-filename
        file_name_with_extension = os.path.basename(self.baseFilename)
        dir_name = os.path.dirname(self.baseFilename)
        deviceName = socket.gethostname()
        time = datetime.datetime.now().isoformat()
        self.baseFilename = '%s_msLog_%s' % (deviceName, time)        
        self.mode = 'w'
        self.stream = self._open()

def setup_logger(name, destination):
    global logger
    logger = logging.getLogger()
    logger.setLevel('DEBUG')
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s %(message)s', datefmt="%m-%d-%Y %H:%M:%S")

    # Add a time-rotating log handler
    ExportedRotatingFileHandler.destination_dir = destination
    logger_handler = ExportedRotatingFileHandler('{}.log'.format(name), maxBytes=10000000, backupCount=10)
    logger_handler.setLevel('INFO')
    logger_handler.setFormatter(formatter)

    # StreamHandler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(logger_handler)
    logger.addHandler(stream_handler)
    return True


def get_logger():
    global logger
    if logger is not None:
        return logger
    else:
        raise ValueError("Logger name not specified! Call set_logger before writing to log")


