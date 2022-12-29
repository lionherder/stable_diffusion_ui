import time
from enum import Enum

class logger_enum(Enum):
	DEBUG = 0
	INFO = 1
	WARN = 2
	ERROR = 3

logger_levels = Enum('logger_enum', ['DEBUG', 'INFO', 'WARN', 'ERROR'])

class SD_Logger():

	def __init__(self, title='', log_level=logger_levels.DEBUG):
		self.title = title
		self.log_level = log_level

	def log(self, msg, level):
		#if (level >= self.log_level):
		print(f"{time.ctime()} [{self.title}] {logger_levels(level).name}: {msg}")

	def debug(self, msg):
		self.log(msg, logger_levels.DEBUG)

	def info(self, msg):
		self.log(msg, logger_levels.INFO)

	def warn(self, msg):
		self.log(msg, logger_levels.WARN)

	def error(self, msg):
		self.log(msg, logger_levels.ERROR)
