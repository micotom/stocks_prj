from sseclient import SSEClient
from django.http.response import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.core.exceptions import ValidationError
from .isininfo import IsinInfo
import requests
import sseclient
import datetime
import logging
import json
import re

epoch = datetime.datetime.utcfromtimestamp(0)

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

def home(request):
    return HttpResponse("Hello!")

def __build_req(from_time: int, to_time: int, mic: str, isin: str) -> str:
    return (
        "https://api.boerse-frankfurt.de/v1/tradingview/lightweight/history"
        "?resolution=M"
        "&isKeepResolutionForLatestWeeksIfPossible=false"
        f"&from={from_time}"
        f"&to={to_time}"
        "&isBidAskPrice=false"
        f"&symbols={mic}:{isin}"
    )

def __create_see_client(url: str) -> SSEClient:
    resp = requests.get(url, stream=True)
    client = sseclient.SSEClient(resp)
    return client     

def __capture_data(client: SSEClient):
    data = None
    for e in client.events():
        # Ignore keep alive events.
        logger.debug(f"data: {e.data}")
        if not e.data == "health_event":
            data = e.data
            break  
    client.close()
    return data       

__isin_regex = re.compile(r'([A-Z]{2})([A-Z0-9]{9})([0-9]{1})')
def validateIsin(isin) -> bool:
    match = __isin_regex.match(str(isin))
    return bool(match)

__days_refex = re.compile(r'^[0-9]*$')
def validateDays(days) -> bool:
    match = __days_refex.match(str(days))
    return bool(match)

def get_data(request):

    isin: str = request.GET['isin']
    mic: str = request.GET['mic']
    days: int = int(request.GET['days'])

    if not validateIsin(isin):
        raise ValidationError("Invalid Isin", code=400, params={'value': isin})
    if not mic == "XETR":
        raise ValidationError("Invalid Mic", code=400, params={'value': mic})
    if not validateDays(days):
        raise ValidationError("Invalid Days", code=400, params={'value': days})
        
    to_time_raw = datetime.datetime.now()
    from_time_raw = to_time_raw - datetime.timedelta(days = days)
    to_time: int = int((to_time_raw - epoch).total_seconds())
    from_time: int = int((from_time_raw - epoch).total_seconds())

    url: str = __build_req(from_time, to_time, mic, isin)
    logger.debug(f"URL REQUEST: {url}")
    client = __create_see_client(url)
    data = __capture_data(client)
    logger.error(f"{data}")

    resultDict = json.loads(data)
    result = IsinInfo(resultDict['isin'], resultDict['mic'], resultDict['isUpdateWithoutHistory'], resultDict['quotes'])

    format: str = request.GET['format']
    if format == 'json':
        return JsonResponse(result.to_dict(), safe=False)
    else:    
        return HttpResponseBadRequest()