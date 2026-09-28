import logging

logger = logging.getLogger("health_check_logger")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
formatter.datefmt = '%Y-%m-%d %H:%M:%S'

file_handler = logging.FileHandler('health_check.log', mode='a')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
