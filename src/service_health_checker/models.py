from .logging_config import logger

def CheckResult(
        service: str,
        check_type: str, 
        success: bool, 
        duration: float, 
        details: dict = {},
        error: str = ""):
    if check_type == 'dns':
        if success == True:
            logger.info(f"DNS check passed: {service} {details["ip_address"]} {duration:.2f}s")
        else:
            logger.error(f"DNS check failed: {service} {duration:.2f}s {error}")

    if check_type == 'tcp':
        if success == True:
            logger.info(f"TCP check passed: {service} {duration:.2f}s")
        else:
            logger.error(f"TCP check failed: {service} {duration:.2f}s {error}")

    if check_type == 'http':
        if success == True:
            logger.info(f"HTTP check passed: {service} 200 {duration:.2f}s")
        else:
            logger.error(f"HTTP check failed: {service} {details['status_code']} {duration:.2f}s")
