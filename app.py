import streamlit as st
import pandas as pd
from openai import OpenAI
import json

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
    
    # [5단계 점수 체계 완벽 복원] 시스템 프롬프트
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이야. 아래의 5단계 리스크 점수 체계를 엄격히 준수하여 '중간 점수'의 균형을 맞춰라.\n\n"
        "### 📊 5단계 리스크 판정 가이드\n"
        "1. **Level 5 (90-100점)**: 원색적 욕설(씨발 등), 반인륜적 모독, 중대 범죄(성범죄 등) 직접 연루 단어.\n"
        "2. **Level 4 (80-89점)**: 명확한 비하/조롱 의도가 담긴 혐오 밈 (흉자 등).\n"
        "3. **Level 3 (60-79점)**: 강한 비속어 변형, 공격적인 유행어, 과도한 낙관주의 조롱(가즈아 등).\n"
        "4. **Level 2 (40-59점)**: 경미한 비하, 지능/외모를 낮잡아 보는 표현 (머저리 등).\n"
        "5. **Level 1 (0-39점)**: 단순 인터넷 밈(오조오억, 쵸키포키 등), 일상적 감탄사, 무해한 유머.\n\n"
        "### ⚠️ 주의사항\n"
        "- '오조오억'과 같은 단순 수치 과장 밈을 90점대(Level 5)로 판정하는 것은 중대한 오류다. 반드시 10~20점대(Level 1)로 판정해라.\n"
        "- 실제 인물 사건(앱스타인 등)은 단순 밈이 아닌 '사회적 사실'에 기반하여 90점 이상으로 상세히 설명해라."
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
            
            # [자동 밸런스 조정 레이어]
            score = res.get('부정점수', 0)
            bg = res.get('논란의배경', '')
            
            # 1. 원형 욕설 강제 상향 (95점)
            if any(k in bg for k in ["원색적 욕설", "직설적 욕설"]):
                score = max(score, 95)
            # 2. 무해한 밈 강제 하향 (10~20점)
            if any(k in bg for k in ["단순 과장", "무해한", "수치 표현", "오조오억"]):
                score = min(score, 20)
                
            res['부정점수'] = score
            return res
        except: return None

    def display_result(word, res):
        score = res.get('부정점수', 0)
        st.divider()
        st.success(f"'{word}' 분석 완료")
        
        # 이전 UI: 리스크 점수와 카테고리 태그
        c1, c2 = st.columns([1, 2])
        with c1: st.metric("리스크 점수", f"{score}점")
        with c2: st.subheader(f"🏷️ {res.get('카테고리', '미분류')}")
        
        st.progress(score/100)
        
        st.info(f"📖 **표면적 의미:** \n\n {res.get('표면적의미', '')}")
        
        # 점수에 따른 카드 색상 변화 (이전 스타일)
        if score >= 90:
            st.error(f"🚨 **상세 맥락 및 배경 (고위험/범죄 사실):** \n\n {res.get('논란의배경', '')}")
        elif score >= 60:
            st.warning(f"⚠️ **상세 맥락 및 배경 (사회적 논란/비하):** \n\n {res.get('논란의배경', '')}")
        else:
            st.success(f"✅ **상세 맥락 및 배경 (일반/무해):** \n\n {res.get('논란의배경', '')}")
            
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 메인 화면
    word_input = st.text_input("분석할 단어 입력:")
    if st.button("분석 실행"):
        with st.spinner('이전 5단계 기준에 따라 정밀 분석 중...'):
            res = analyze_word(word_input)
            if res: display_result(word_input, res)

else:
    st.info("API 키를 입력해주세요.")
