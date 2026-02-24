import streamlit as st
from openai import OpenAI
import json

# 1. 검증된 핵심 데이터베이스 (AI의 자의적 해석 방지용)
VERIFIED_DATA = {
    "흉자": {
        "score": 85, "cat": "비하/조롱 밈",
        "meaning": "'흉내자지'의 줄임말로, 가부장적 가치관을 따르는 여성을 조롱하는 혐오 표현.",
        "bg": "특정 온라인 커뮤니티(워마드 등)에서 유래하여 사상에 동조하지 않는 여성을 공격하는 용도로 사용됨."
    },
    "피떡갈비": {
        "score": 92, "cat": "고인 모독/반인륜적 밈",
        "meaning": "현대사 비극적 사건 희생자들을 잔인하게 비하하고 조롱하는 패륜적 표현.",
        "bg": "시신을 음식에 비유하는 극히 악의적인 고인 모독 맥락을 담고 있음."
    },
    "오조오억": {
        "score": 85, "cat": "문화 이슈",
        "meaning": "수량이 매우 많음을 뜻하나, 현재는 특정 집단 조롱의 의미로 변질된 표현.",
        "bg": "단순 과장 표현을 넘어 젠더 갈등의 상징적 단어로 사용되며 사회적 논란을 유발함."
    }
}

st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'): 
            # [Step 1] 검증된 데이터가 있는지 먼저 확인 (환각 원천 차단)
            if word_input in VERIFIED_DATA:
                data = VERIFIED_DATA[word_input]
                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{data['score']}점")
                with c2: st.subheader(f"🏷️ {data['cat']}")
                st.info(f"📖 **표면적 의미:** \n\n {data['meaning']}")
                st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {data['bg']}")
                st.info(f"⚖️ **정책 판단 근거:** 커뮤니티 내 명확한 비하 의도가 확인되어 정책적 관리가 필요함.")
            
            # [Step 2] 새로운 단어인 경우만 AI 분석 진행
            else:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": "너는 온라인 혐오 표현 전문가야. 사전적 의미보다 커뮤니티 조롱 맥락을 우선해."},
                                  {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}],
                        response_format={ "type": "json_object" },
                        temperature=0
                    )
                    result = json.loads(response.choices[0].message.content)
                    st.divider(); st.success("분석 완료")
                    st.metric("리스크 점수", f"{result['부정점수']}점")
                    st.write(f"🏷️ {result['카테고리']}")
                    st.info(f"📖 의미: {result['표면적의미']}")
                    st.warning(f"⚠️ 배경: {result['논란의배경']}")
                except Exception:
                    st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
