from dotenv import load_dotenv
import os
import json
import urllib.request
import streamlit as st
import pandas as pd

load_dotenv()

NaverId = os.getenv("NaverId") or st.secrets["NaverId"]
NaverSecret = os.getenv("NaverSecret") or st.secrets["NaverSecret"]

st.title("뉴스 검색하기")

text = st.text_input("검색어 입력")
StartDate = st.date_input("시작 날짜 입력")
EndDate = st.date_input("끝 날짜 입력")

SearchHistory = text + " : " + StartDate.strftime("%y년 %m월 %d일") + "~" + EndDate.strftime("%y년 %m월 %d일")

# session_state 초기화
if "history" not in st.session_state:
    st.session_state["history"] = []


if st. button("검색하기") and text:

    # 입력한 검색어 바꿔서 url에 붙이기
    encText = urllib.parse.quote(text)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display=100"

    # 검색하기
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", NaverId)
    request.add_header("X-Naver-Client-Secret", NaverSecret)


    # 검색 기록 저장
    st.session_state["history"].append(SearchHistory)

    try:
        with urllib.request.urlopen(request) as response:
            # 정상적으로 검색됐는지 검사
            rescode = response.getcode()
            if rescode == 200:

                # 복호화하기, 타입 변환해주기
                ResponseBody = response.read()
                ResponseResult = ResponseBody.decode("utf-8")
                ResponseResult = json.loads(ResponseResult)

                items = ResponseResult.get("items", [])

                if items:
                    df = pd.DataFrame(items)

                    # 날짜 형식을 바꿔주기
                    df["pubDate"] = pd.to_datetime(df["pubDate"], format = "%a, %d %b %Y %H:%M:%S %z")
                    
                    # 날짜 필터링
                    FilteredDf = df[
                        (df["pubDate"].dt.date >= StartDate) & (df["pubDate"].dt.date <= EndDate)
                    ]

                    if len(FilteredDf) == 0:
                        st.info("검색 결과가 없습니다.")

                    else:
                        # 검색 결과가 있으면 출력해주기
                        st.write(f"{StartDate}부터 {EndDate}까지 {text}키워드로 {len(FilteredDf)}개의 뉴스가 작성되었습니다.")
                        st.dataframe(FilteredDf)
                    
                else:
                    st.info("검색 결과가 없습니다.")
            else:
                st.error(f"API 호출 실패. 응답코드 : {rescode}")
    except Exception as e:
        st.error(f"오류 발생 : {e}")

st.subheader("검색 기록")

# 검색 기록 업데이트해주기
for history in st.session_state["history"]:
    st.write(history)
    
# 검색 기록 지우기
if st.button("기록 삭제"):
    st.session_state.clear()

