import math

import matplotlib.pyplot as plt
import streamlit as st

from ai_helper import ask_ai
from air_api import get_sido, get_station

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

SIDOS = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
         "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주"]
GRADES = {"1": "좋음", "2": "보통", "3": "나쁨", "4": "매우나쁨"}


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def grade_label(code):
    return GRADES.get(str(code), "정보없음")


@st.cache_data(ttl=600)
def load_stations(sido):
    return sorted({item["stationName"] for item in get_sido(sido)})


@st.cache_data(ttl=600)
def load_today(station):
    items = get_station(station)
    return sorted(items, key=lambda item: item["dataTime"])


def draw_chart(station, items):
    times = [item["dataTime"][-5:] for item in items]
    pm10 = [num(item["pm10Value"]) for item in items]
    pm25 = [num(item["pm25Value"]) for item in items]

    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(times, pm10, marker="o", label="PM10")
    ax.plot(times, pm25, marker="o", label="PM2.5")
    ax.set_title(f"{station} 오늘 측정 추이")
    ax.set_ylabel("㎍/㎥")
    ax.grid(alpha=0.3)
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


st.set_page_config(page_title="미세먼지 알림")
st.title("미세먼지 알림")

col_sido, col_station = st.columns(2)
with col_sido:
    sido = st.selectbox("시·도", SIDOS)

stations = load_stations(sido)
with col_station:
    station = st.selectbox("측정소", stations, disabled=not stations)

if not stations:
    st.warning("해당 지역의 측정소 목록을 가져오지 못했습니다. API 키와 네트워크를 확인해 주세요.")

if st.button("조회", type="primary", disabled=not stations):
    with st.spinner("측정값을 조회하고 AI 안내를 만드는 중입니다..."):
        items = load_today(station)
        valid = [item for item in items
                 if not (math.isnan(num(item["pm10Value"])) and math.isnan(num(item["pm25Value"])))]

        if not valid:
            st.warning("오늘 측정값이 없습니다.")
        else:
            latest = valid[-1]
            pm10_grade = grade_label(latest.get("pm10Grade"))
            pm25_grade = grade_label(latest.get("pm25Grade"))

            st.caption(f"{station} · 측정 시각 {latest['dataTime']}")
            m1, m2 = st.columns(2)
            m1.metric("PM10 (미세먼지)", f"{latest['pm10Value']} ㎍/㎥",
                      delta=pm10_grade, delta_color="off")
            m2.metric("PM2.5 (초미세먼지)", f"{latest['pm25Value']} ㎍/㎥",
                      delta=pm25_grade, delta_color="off")

            draw_chart(station, items)

            prompt = (
                f"다음은 {station} 측정소의 {latest['dataTime']} 기준 미세먼지 측정값입니다.\n"
                f"PM10: {latest['pm10Value']} ㎍/㎥ ({pm10_grade})\n"
                f"PM2.5: {latest['pm25Value']} ㎍/㎥ ({pm25_grade})\n"
                "일반 시민에게 외출, 마스크 착용 등 행동 요령을 한국어 2~3문장으로 안내해 주세요."
            )
            advice = ask_ai(prompt)
            with st.container(border=True):
                st.markdown("#### AI 안내")
                st.write(advice)
