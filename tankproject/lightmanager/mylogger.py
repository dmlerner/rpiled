import logging
import datetime


class Logger:
    def __init__(self, enable=True, stdout=True, default_level="info", name=""):
        self.enable = enable
        self.stdout = stdout
        self.logger = logging.getLogger(name)

    def log(self, *args):
        if not self.enable:
            return
        stuff = (
            file_name,
            line_number,
            function_name,
            stack_info,
        ) = self.logger.findCaller(stacklevel=2)
        timestamp = datetime.datetime.now()
        log_str = f"[{timestamp}] | " + " | ".join(map(str, args))
        self.logger.info(log_str)
        if self.stdout:
            print(log_str)
