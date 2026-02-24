import streamlit as st
from openai import OpenAI
import json

# 1. 마스터 데이터베이스 (핵심 논란 단어 고정)
KNOWLEDGE_BASE = {
    "흉자": {
        "score": 85, "cat": "비하/조롱 밈",
        "meaning": "'흉내자지'의 줄임말로, 가부장적 가치관을 따르는 여성을 비하하는 혐오 표현.",
        "bg": "특정 온라인 커뮤니티 유래. 사상에 동조하지 않는 여성을 공격하는 용도로 사용됨."
    },
    "피떡갈비": {
        "score": 92, "cat": "고인 모독/반인륜적 밈",
        "meaning": "현대사 비극적 사건 희생자들을 잔인하게 비하하고 조롱하는 패륜적 표현.",
        "bg": "시신을 음식에 비유하는 극히 악의적인 맥락을 담고 있음."
    },
    "오조오억": {
        "score": 85, "cat": "문화 이슈",
        "meaning": "수량이 매우 많음을 뜻하나, 현재는 특정 집단 조롱의 의미로 변질된 표현.",
        "bg": "젠더 갈등의 상징적 단어로 사용되며 사회적 논란을 유발함."
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
            # [Step 1] 고정 DB 확인
            if word_input in KNOWLEDGE_BASE:
                data = KNOWLEDGE_BASE[word_input]
                st.divider()
                st.success("심층 분석 완료 (검증된 데이터)")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{data['score']}점")
                with c2: st.subheader(f"🏷️ {data['cat']}")
                st.info(f"📖 **표면적 의미:** \n\n {data['meaning']}")
                st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {data['bg']}")
            
            # [Step 2] '쵸키포키' 등 새로운 신조어 정밀 분석
            else:
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책관이야. '쵸키포키'와 같은 신조어 분석 시 아래 규칙을 따라.\n"
                                "1. 단순 밈이라도 '조롱', '경멸', '비하'의 뉘앙스가 있다면 절대 0~20점을 주지 마.\n"
                                "2. 사회적 논란이나 특정 대상에 대한 조롱이 감지되면 최소 70점 이상의 점수를 부여해.\n"
                                "3. 배경 설명에 '어떤 상황에서 왜 조롱으로 쓰이는지'를 아주 구체적으로 서술해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}],
                        response_format={ "type": "json_object" },
                        temperature=0
                    )
                    result = json.loads(response.choices[0].message.content)
                    
                    # [보정 로직] 조롱 뉘앙스 감지 시 점수 자동 상향
                    score = result.get('부정점수', 0)
                    bg = result.get('논란의배경', '')
                    if any(k in bg for k in ["조롱", "경멸", "비하"]) and score < 70:
                        score = 75
                        result['카테고리'] = "비하/조롱 밈"

                    st.divider(); st.success("분석 완료")
                    c1, c2 = st.columns(2)
                    with c1: st.metric("리스크 점수", f"{score}점")
                    with c2: st.subheader(f"🏷️ {result['카테고리']}")
                    st.info(f"📖 의미: {result['표면적의미']}")
                    st.warning(f"⚠️ 배경: {bg}")
                except:
                    st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
