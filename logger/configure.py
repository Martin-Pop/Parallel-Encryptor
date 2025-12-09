import sys, logging, copy

from multiprocessing import Queue
from logging.handlers import QueueListener, QueueHandler


class KeepTraceBackQueueHandler(QueueHandler):
    """
    Slightly edited QueueHandler that keeps the stack trace text for pickling
    """

    def prepare(self, record):
        """
        Prepares record for queueing but keeps exc_text
        :param record: record to prepare
        :return: record object to queue
        """
        saved_info = record.exc_info
        saved_text = record.exc_text

        # must format text separately
        if saved_info and not saved_text:
            saved_text = logging.Formatter().formatException(saved_info)

        record.exc_info = None
        record.exc_text = None

        # format message without any stack trace info
        msg = self.format(record)

        # restore for other handlers
        record.exc_info = saved_info
        record.exc_text = saved_text

        record = copy.copy(record)
        record.message = msg
        record.msg = msg
        record.args = None
        record.exc_info = None
        record.stack_info = None

        return record


class SuppressTracebackFormatter(logging.Formatter):
    """
    Custom formatter that overwrites format function.
    This is because default format function joins record message and exc_text together
    + adds nice color
    """

    def format(self, record):
        msg = super().formatMessage(record)

        if record.levelno >= logging.ERROR:
            msg = f"{"\033[31m"}{msg}{"\033[0m"}"

        return msg


def configure_logger_queue(file_path, suppress_info=False):
    """
    Configures logger handlers for queue logging (QueueListener, QueueHandler)
    :param file_path: log file path
    :param suppress_info: True to disable parameters logging
    :return: multiprocessing queue and QueueListener
    """
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # FILE
    file_handler = logging.FileHandler(file_path, encoding="utf-8", mode='a')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(file_format)

    # CONSOLE
    if not suppress_info:
        console_format = SuppressTracebackFormatter('%(levelname)s - %(message)s')

        console_info_handler = logging.StreamHandler(sys.stdout)
        console_info_handler.setLevel(logging.INFO)
        console_info_handler.setFormatter(console_format)
        console_info_handler.addFilter(lambda record: record.levelno == logging.INFO)

        console_err_handler = logging.StreamHandler(sys.stderr)
        console_err_handler.setLevel(logging.WARNING)
        console_err_handler.setFormatter(console_format)

        handlers = (file_handler, console_info_handler, console_err_handler)
    else:
        handlers = (file_handler,)

    log_queue = Queue()
    listener = QueueListener(log_queue, *handlers, respect_handler_level=True)

    return log_queue, listener


def add_queue_handler_to_root(queue):
    """
    Adds queue to QueueHandler for root logger
    This function is called from processes.
    :param queue: queue through which logs are connected to the same listener
    """
    root = logging.getLogger()
    root.setLevel(logging.NOTSET)
    root.addHandler(KeepTraceBackQueueHandler(queue))