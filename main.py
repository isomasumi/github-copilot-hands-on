from dataclasses import dataclass

import requests
import pandas as pd
import streamlit as st


# 都市名とOpen-Meteo APIで使用する位置情報をひとまとめにする。
@dataclass(frozen=True)
class Location:
	latitude: float
	longitude: float


# セレクトボックスに表示する都市と、その都市の緯度・経度を定義する。
LOCATIONS = {
	"東京": Location(latitude=35.6762, longitude=139.6503),
	"大阪": Location(latitude=34.6937, longitude=135.5023),
}
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
# APIから日別で取得する気象データの項目を定義する。
DAILY_PARAMETERS = [
	"weather_code",
	"temperature_2m_max",
	"temperature_2m_min",
	"precipitation_probability_max",
]

WEATHER_LABELS = {
	0: "快晴",
	1: "晴れ",
	2: "一部曇り",
	3: "曇り",
	45: "霧",
	48: "着氷性の霧",
	51: "弱い霧雨",
	53: "霧雨",
	55: "強い霧雨",
	61: "弱い雨",
	63: "雨",
	65: "強い雨",
	71: "弱い雪",
	73: "雪",
	75: "強い雪",
	80: "弱いにわか雨",
	81: "にわか雨",
	82: "強いにわか雨",
	85: "弱いにわか雪",
	86: "強いにわか雪",
	95: "雷雨",
	96: "ひょうを伴う雷雨",
	99: "強いひょうを伴う雷雨",
}
# 詳細なWMO天気コードを、画面表示用の3分類へ変換するためのコード群。
SUNNY_CODES = {0, 1}
CLOUDY_CODES = {2, 3, 45, 48}


def weather_category(weather_code: int) -> str:
	# 晴れ・曇り以外は、雨や雪などの降水を含むため「雨」に分類する。
	if weather_code in SUNNY_CODES:
		return "晴れ"
	if weather_code in CLOUDY_CODES:
		return "曇り"
	return "雨"


def create_forecast_dataframe(daily_forecast: dict) -> pd.DataFrame:
	# APIレスポンスを、画面の表で扱いやすい日本語のDataFrameへ変換する。
	return pd.DataFrame(
		{
			"日付": pd.to_datetime(daily_forecast["time"]).strftime("%m/%d"),
			"天気区分": [
				weather_category(code) for code in daily_forecast["weather_code"]
			],
			"天気": [
				WEATHER_LABELS.get(code, "不明")
				for code in daily_forecast["weather_code"]
			],
			"最高気温 (℃)": daily_forecast["temperature_2m_max"],
			"最低気温 (℃)": daily_forecast["temperature_2m_min"],
			"降水確率 (%)": daily_forecast["precipitation_probability_max"],
		}
	)


@st.cache_data(ttl=3600)
def fetch_forecast(latitude: float, longitude: float) -> pd.DataFrame:
	"""Open-Meteoから7日間予報を取得して表形式に変換する。"""
	# 東京または大阪の位置情報を指定して、タイムゾーン付きの7日予報を取得する。
	parameters = {
		"latitude": latitude,
		"longitude": longitude,
		"daily": DAILY_PARAMETERS,
		"timezone": "Asia/Tokyo",
		"forecast_days": 7,
	}
	response = requests.get(OPEN_METEO_URL, params=parameters, timeout=10)
	response.raise_for_status()
	# APIから取得した日別データを表示用のDataFrameへ変換する。
	return create_forecast_dataframe(response.json()["daily"])


# Streamlit画面の基本設定と都市選択欄を表示する。
st.set_page_config(page_title="週間天気予報", page_icon="☀️", layout="wide")

selected_location = st.selectbox("都市を選択", list(LOCATIONS))
location = LOCATIONS[selected_location]

st.title(f"{selected_location}の週間天気予報")
st.caption("Open-Meteoの予報データを使用しています。")

try:
	forecast = fetch_forecast(location.latitude, location.longitude)
except (requests.RequestException, KeyError, ValueError) as error:
	# 通信エラーや想定外のレスポンスでも、画面に内容を表示して安全に終了する。
	st.error(f"天気予報を取得できませんでした: {error}")
	st.stop()

# 選択した都市の当日予報を、画面上部のメトリクスで強調表示する。
today = forecast.iloc[0]
metric_columns = st.columns(3)
metric_columns[0].metric("今日の天気", today["天気"])
metric_columns[1].metric("最高気温", f"{today['最高気温 (℃)']:.1f} ℃")
metric_columns[2].metric("降水確率", f"{today['降水確率 (%)']:.0f} %")

st.subheader("7日間の予報")
# 7日分の天気分類、詳細天気、気温、降水確率を表形式で表示する。
st.dataframe(forecast, hide_index=True, use_container_width=True)

st.subheader("気温の推移")
# 7日間の最高気温と最低気温を折れ線グラフで表示する。
temperature_chart = forecast.set_index("日付")[["最高気温 (℃)", "最低気温 (℃)"]]
st.line_chart(temperature_chart)
