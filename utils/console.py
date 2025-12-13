import logging, sys
log = logging.getLogger(__name__)

def resolve_yes_no(message, log_level ,default=False):
    """
    Resolve yes/no questions.
    :param log_level: level of log message
    :param message: message to display
    :param default: default answer (False if not specified)
    :return: True if answer is yes, False if answer is no, otherwise default
    """
    log_fn = getattr(log, log_level, log.info)
    log_fn(message)
    yes_no = input().strip().lower()

    if yes_no == 'y':
        return True
    elif yes_no == 'n':
        return False
    else:
        return default
