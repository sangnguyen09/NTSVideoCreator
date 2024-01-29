import inspect
import logging
import os
import sys
import traceback
from datetime import time, datetime

from gui.helpers.constants import PATH_LOGS


def customLogger(func_name,lineno=None):
    # 1.) This is used to get the  class / method name from where this customLogger method is called
    logName = inspect.stack()[1][3]

    # 2.) Create the logging object and pass the logName in it
    logger = logging.getLogger(logName)

    # 3.) Set the Log level
    logger.setLevel(logging.DEBUG)
    app_path = os.path.abspath(os.getcwd())
    # folder = "logs/"
    path = os.path.join(app_path, PATH_LOGS)
    file_log =os.path.normpath(os.path.join(path, "logs.txt"))
    
    if os.path.exists(file_log) is False:
        with open(file_log, 'w') as f:
            pass
    size =os.path.getsize(file_log)
    if size > 1000000 :
        if os.path.exists(file_log):
            os.remove(file_log)
    # 4.) Create the fileHandler to save the logs in the file
    fileHandler = logging.FileHandler(file_log, mode='a')

    # 5.) Set the logLevel for fileHandler
    fileHandler.setLevel(logging.DEBUG)

    # 6.) Create the formatter in which format do you like to save the logs
    # formatter = logging.Formatter(f'%(levelname)s: %(asctime)s - %(name)s - %(filename)s - %(funcName)s():%(lineno)d %(message)s',
    #                               datefmt='%d/%m/%y %I:%M:%S %p %A')
    # 6.) Create the formatter in which format do you like to save the logs
    formatter = logging.Formatter(f'%(levelname)s: %(asctime)s - {func_name} %(message)s',
                                  datefmt='%d/%m/%y %I:%M:%S %p %A')

    # 7.) Set the formatter to fileHandler
    fileHandler.setFormatter(formatter)

    # 8.) Add file handler to logging
    logger.addHandler(fileHandler)

    #  9.) Finally return the logging object

    return logger


def customFfmpegLogger(name_file):
    # 1.) This is used to get the  class / method name from where this customLogger method is called
    logName = inspect.stack()[1][3]

    # 2.) Create the logging object and pass the logName in it
    logger = logging.getLogger(logName)

    # 3.) Set the Log level
    logger.setLevel(logging.DEBUG)
    app_path = os.path.abspath(os.getcwd())
    
    path = os.path.join(app_path, PATH_LOGS)
    file_log =os.path.normpath(os.path.join(path, name_file +".txt"))
    
    if os.path.exists(file_log) is False:
        with open(file_log, 'w') as f:
            pass
    # size =os.path.getsize(file_log)
    # if size > 1000000 :
    #     if os.path.exists(file_log):
    #         os.remove(file_log)
    # 4.) Create the fileHandler to save the logs in the file
    fileHandler = logging.FileHandler(file_log, mode='w')

    # 5.) Set the logLevel for fileHandler
    fileHandler.setLevel(logging.DEBUG)

    # 6.) Create the formatter in which format do you like to save the logs
    # formatter = logging.Formatter(f'%(levelname)s: %(asctime)s - %(name)s - %(filename)s - %(funcName)s():%(lineno)d %(message)s',
    #                               datefmt='%d/%m/%y %I:%M:%S %p %A')
    
    # 6.) Create the formatter in which format do you like to save the logs
    # formatter = logging.Formatter(f'%(levelname)s: %(asctime)s - {func_name}:{lineno} %(message)s',
    #                               datefmt='%d/%m/%y %I:%M:%S %p %A')
    # 6.) Create the formatter in which format do you like to save the logs
    formatter = logging.Formatter(f'%(levelname)s: %(asctime)s %(message)s',
                                  datefmt='%d/%m/%y %I:%M:%S %p %A')

    # 7.) Set the formatter to fileHandler
    fileHandler.setFormatter(formatter)

    # 8.) Add file handler to logging
    logger.addHandler(fileHandler)

    #  9.) Finally return the logging object

    return logger


def decorator_try_except_class(function_run):
    # Wrapper nhận mọi tham số đầu vào
    def wrapper_function(self, *args, **kwargs):
        try:
            return function_run(self, *args, **kwargs)

        except Exception as e:
            try:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                # print ("E=%s, F=%s, L=%s" % (str(e), traceback.extract_tb(exc_tb)[-1][0] )
                customLogger(function_run.__name__,traceback.extract_tb(exc_tb)[-1][1]).error(str(e))
            finally:
                e = None
                del e
    return wrapper_function

if __name__ == "__main__":
    print()
    customLogger().warning("hay hay")
