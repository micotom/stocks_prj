import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class IsinInfo(object):
    def __init__(self, isin, mic, isUpdateWithoutHistory, quote):
        self.isin = isin
        self.mic = mic
        self.isUpdateWithoutHistory = isUpdateWithoutHistory
        self.quote = Quote(quote['count'], quote['timeValuePairs'])

    def to_dict(self):
        return { 'isin': self.isin, 'quotes': self.quote.to_dict()}

class Quote(object):
    def __init__(self, count, timeValuePairs):
        self.count = count
        self.timeValuePairs = list(map(mapValuePairs, timeValuePairs))
    
    def to_dict(self):
        return list(map(lambda pair: pair.to_dict(), self.timeValuePairs))

class TimeValuePair(object):
    def __init__(self, time, value):
        self.time = time
        self.value = value
    def __str__(self) -> str:
        return f"{self.time}: {self.value}"
    def to_dict(self):
        return { 'time': self.time, 'value': self.value }        

def mapValuePairs(pair) -> TimeValuePair:
    time = datetime.fromtimestamp(pair['time']).strftime("%d.%m.%Y")
    return TimeValuePair(time, pair['value'])
