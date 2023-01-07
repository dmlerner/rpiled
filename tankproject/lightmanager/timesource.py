import datetime


class TimeSource:
    def __init__(self, mock=False, now=None, today=None):
        self.mock = mock
        self.now = now
        self.today = today
        if mock:
            assert self.get_midnight() < self.get_now()
            assert self.get_now() - self.get_midnight() < datetime.timedelta(days=1)

    def get_now(self):
        if not self.mock:
            return datetime.datetime.now()
        return self.now

    def get_today(self):
        if not self.mock:
            return datetime.date.today()
        return self.today

    def get_midnight(self):
        return datetime.datetime.combine(
            self.get_today(),
            datetime.datetime.min.time(),
        )

    def get_time_since_midnight(self):
        return self.get_now() - self.get_midnight()
