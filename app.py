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
    
    # [이전 버전의 상세 정보 조회 기준 복원] 시스템 프롬프트
    SYSTEM_PROMPT = (
        "너는 글로벌 정책 결정관이자 온라인 커뮤니티 언어 전문가야. 아래 수칙에 따라 단어를 정밀 분석해.\n\n"
        "### [1. 상세 정보 조회 가이드 - 필수]\n"
        "- 단어를 단순히 사전적으로 풀이하지 말고, '실제 온라인 커뮤니티(디시, 더쿠, 에펨 등)에서 어떤 맥락으로 쓰이는가'를 최우선으로 분석해라.\n"
        "- 특히 '오조오억'이나 '웅앵웅' 같은 단어는 단순 수치 과장이나 의성어를 넘어, 특정 집단 간의 갈등(젠더 갈등 등)이나 비하의 의도로 사용되는 현재의 사회적 논란을 상세히 서술해라.\n"
        "- 배경 설명에 '어떤 커뮤니티에서 유래했는지', '왜 사회적으로 문제가 되었는지'를 반드시 포함해라.\n\n"
        "### [2. 5단계 리스크 판정 기준]\n"
        "1. Level 5 (90-100점): 원색적 욕설, 반인륜적 모독, 중대 범죄 사실.\n"
        "2. Level 4 (80-89점): 명확한 비하/조롱 의도가 담긴 혐오 밈 (흉자 등).\n"
        "3. Level 3 (60-79점): 강한 비속어 변형, 공격적인 유행어.\n"
        "4. Level 2 (40-59점): 경미한 비하 표현.\n"
        "5. Level 1 (0-39점): 단순 인터넷 밈, 일상어 변형. (단, 논란이 있다면 배경에 상세 기술)"
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
            
            # 고위험군 보정 로직 유지
            score = res.get('부정점수', 0)
            bg = res.get('논란의배경', '')
            if any(k in bg for k in ["원색적 욕설", "직설적 욕설"]): score = max(score, 95)
            if any(k in bg for k in ["성범죄", "사건", "연루"]): score = max(score, 92)
            
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
        
        # 상세 맥락 가시성 강화
        if score >= 80:
            st.error(f"🚨 **상세 맥락 및 배경 (사회적 논란 및 유래):** \n\n {res.get('논란의배경', '')}")
        else:
            st.warning(f"⚠️ **상세 맥락 및 배경 (커뮤니티 사용 맥락):** \n\n {res.get('논란의배경', '')}")
            
        st.info(f"⚖️ **정책 판단 근거:** \n\n {res.get('판단근거', '')}")

    # 메인 분석 실행
    word_input = st.text_input("분석할 단어 입력:")
    if st.button("분석 실행"):
        # 요청하신 대로 문구 변경
        with st.spinner('분석 중...'):
            res = analyze_word(word_input)
            if res: display_result(word_input, res)

else:
    st.info("API 키를 입력해주세요.")
