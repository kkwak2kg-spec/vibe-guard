import streamlit as st
import pandas as pd
from openai import OpenAI
import json
import base64
from io import BytesIO
from PIL import Image

# 1. 페이지 설정 및 이전 UI 스타일 유지
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍", layout="wide")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 설정
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    
    # [완벽 복원] 고위험군 리스크 판정 및 구체적 정보 조회 시스템 프롬프트
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 사회 문제 분석 전문가야. 아래 수칙을 절대적으로 준수해.\n\n"
        "### [1. 고위험군 점수 정책 - 절대 엄수]\n"
        "- **원형 욕설 (씨발 등)**: 변형되지 않은 원색적 욕설은 반드시 **95~100점**을 부여하고 [욕설/비속어]로 분류해라. 70점대는 중대한 오류다.\n"
        "- **중대 범죄/사건 (앱스타인 등)**: 성범죄, 인명피해, 고인 모독과 관련된 단어는 반드시 **92~95점**을 부여해라. 단순 밈으로 치부하지 마라.\n\n"
        "### [2. 정보 조회 및 설명 기준]\n"
        "- **구체적 사실 적시**: 단어 설명 시 '인터넷 밈'이라는 표현 뒤에 숨지 말고, 실제 범죄 사실, 가해자/피해자 관계, 역사적 사건 등 구체적인 정보를 상세히 서술해라.\n"
        "- **맥락 우선**: 사전적 의미보다 사회적 통념상 인지되는 실제 사건의 본질을 최우선으로 기재해라.\n\n"
        "### [3. 리스크 5단계 세분화 가이드]\n"
        "1. Level 5 (90~100점): 직설적 욕설 원형, 중대 범죄 사건, 반인륜적 모독.\n"
        "2. Level 4 (80~89점): 특정 집단/성별에 대한 강한 혐오 및 비하 밈.\n"
        "3. Level 3 (60~79점): 욕설의 변형어 및 강한 비속어.\n"
        "4. Level 2 (40~59점): 경미한 비하 표현 (머저리 등).\n"
        "5. Level 1 (0~39점): 일상적 유머, 태도 묘사 (비아냥, 가즈아 등)."
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
            
            # [강력 보정 레이어] 이전 버전의 완벽한 기준 복원
            score = res.get('부정점수', 0)
            bg = res.get('논란의배경', '')
            
            # 직설적 욕설 복원
            if any(k in bg for k in ["원색적", "직설적", "원형 욕설"]):
                score = max(score, 95)
                res['카테고리'] = "욕설/비속어"
            
            # 범죄 및 사회적 중대 이슈 복원
            if any(k in bg for k in ["범죄", "성범죄", "성착취", "사건", "연루"]):
                score = max(score, 92)
                res['카테고리'] = "고위험 사회적 이슈"
                
            res['부정점수'] = score
            return res
        except: return None

    def display_result(word, res):
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        
        st.progress(score/100)
        
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        # 고위험군은 에러(빨간색) UI로 강렬하게 표시
        if score >= 90:
            st.error(f"🚨 **상세 맥락 및 배경 (고위험 사실 관계):** \n\n {res.get('논란의배경', '')}")
        else:
            st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {res.get('논란의배경', '')}")
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 탭 구성 (이전 UI 복원)
    tab1, tab2, tab3 = st.tabs(["🔍 단일 검토", "📂 CSV 일괄 검토", "🖼️ 이미지 분석"])

    with tab1:
        word_input = st.text_input("분석할 단어 입력:", key="single_input")
        if st.button("분석 실행", key="single_btn"):
            with st.spinner('구체적인 사건 배경과 원형 욕설 수위를 분석 중...'):
                res = analyze_word(word_input)
                if res: display_result(word_input, res)

    # ... [Tab 2, Tab 3 로직 유지] ...
else:
    st.info("API 키를 입력해주세요.")
