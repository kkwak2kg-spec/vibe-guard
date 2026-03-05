import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import base64
from io import BytesIO
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍", layout="wide")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 설정
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    # [복원된] 시스템 프롬프트: 구체적 사실 적시 및 맥락 강화
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 사회 문제 분석 전문가야. 단어 분석 시 아래 수칙을 지켜.\n\n"
        "1. **구체적 사실 적시**: '앱스타인'과 같이 실제 인물이나 사건이 배경인 경우, '조롱하는 변형어'라는 추상적 표현 대신 실제 성범죄 사건, 역사적 비극 등 구체적인 팩트를 배경 설명에 포함해라.\n"
        "2. **리스크 등급**: 단순 밈이 아닌 범죄, 성착취, 패륜 등과 연관된 경우 무조건 Level 5(90~100점)로 분류해라.\n"
        "3. **표면적 의미**: 단어의 사전적 의미보다 사회적 통념상 인지되는 실제 사건의 본질을 기재해라.\n"
        "4. **정책 판단 근거**: 이 단어가 왜 금칙어로서 관리되어야 하는지 사회적 파장과 피해자 보호 관점에서 서술해라."
    )

    def analyze_word(word):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"'{word}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                ],
                response_format={ "type": "json_object" },
                temperature=0
            )
            res = json.loads(response.choices[0].message.content)
            
            # 동적 보정: 범죄/성범죄/패륜 키워드 감지 시 리스크 상향
            bg = res.get('논란의배경', '')
            if any(k in bg for k in ["범죄", "성범죄", "성착취", "패륜", "사망"]):
                res['부정점수'] = max(res.get('부정점수', 0), 92)
                res['카테고리'] = "고위험 사회적 이슈"
            
            return res
        except: return None

    # 기존 UI 스타일의 출력 함수
    def display_result(word, res):
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 심층 분석 완료")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        
        st.progress(score/100)
        
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        st.error(f"⚠️ **상세 맥락 및 배경 (구체적 사건 중심):** \n\n {res.get('논란의배경', '')}")
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single_input")
        if st.button("분석 실행", key="single_btn"):
            with st.spinner('구체적인 사건 배경과 맥락을 추적 중...'):
                res = analyze_word(word_input)
                if res: display_result(word_input, res)

    # ... [Tab 2, Tab 3 로직은 이전과 동일하게 유지] ...

else:
    st.info("API 키를 입력해주세요.")
