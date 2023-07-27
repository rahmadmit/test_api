from datetime import datetime
from html.parser import HTMLParser
from sqlalchemy.ext.asyncio import AsyncSession

from .model import NewsBuilder

class CustomParser(HTMLParser):
    parse_counter = 0
    builder = NewsBuilder()

    def __init__(self, last_date: datetime):
        self.last_date = last_date
        super().__init__()

    def handle_data(self, data: str):
        
        data = data.strip()
        if not data:
            return

        if self.parse_counter == 0:
            try:
                d_stamp = datetime.strptime(data, "%d.%m.%Y").date()
            except ValueError:
                return
            self.builder.set_date(d_stamp)
            self.parse_counter += 1

        elif self.parse_counter == 1:
            try:
                t_stamp = datetime.strptime(data, '%H:%M').time()
            except ValueError:
                t_stamp = datetime(1,1,1,0,0,0).time()
            self.builder.set_time(t_stamp)
            if not self.builder.check_date(self.last_date):
                self.parse_counter = -1
            self.parse_counter += 1

        elif self.parse_counter == 2:
            self.builder.set_text(data)
            self.builder.push()
            self.parse_counter = 0