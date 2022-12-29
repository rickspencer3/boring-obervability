from app.extensions import db, logger

def notify(notification, check, response):
    logger.info(f"running notification {notification.id} of type {notification.type} for check {check.id}")
    if notification.type == "error":
        _compare(notification, response, check.id)
    if notification.type == "latency":
        pass

def _compare(notification, response, check_id):
    if response.status_code >= int(notification.value):
        logger.info(f"notification {notification.id} conditions met for check {check_id}")
    else:
        logger.info(f"notification {notification.id} conditions not metfor check {check_id}")
