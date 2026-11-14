import os, requests
from dotenv import load_dotenv

load_dotenv()
BASE = "https://apis.data.go.kr/B552584/ArpltnInforInqireSvc"

def call(path, **params):
    params.update(serviceKey=os.getenv("DATA_API_KEY"), returnType= "json", ver="1.3")
    res = requests.get(BASE + path, params=params, timeout=10)
    return res.json()["response"]["body"]["items"]

def get_sido(sido):
    return call("/getCtprvnRltmMesureDnsty", sidoName=sido, numOfRows=100)

def get_station(station):
    return call("/getMsrstnAcctoRltmMesureDnsty", stationName=station, dataTerm="DAILY")