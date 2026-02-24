import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 로드
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정이 필요합니다", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **일상어 보호 원칙**: '사과', '포도', '하늘' 등 사전적 의미가 압도적으로 일상적이고 무해한 단어는 0-30점 사이의 낮은 점수를 부여해. 비하 맥락으로 쓰일 '가능성'만으로 80점 이상의 고득점을 주지 마.\n"
                                    "2. **점수 변별력**: \n"
                                    "   - 직접적 욕설(씨발 등): 90-100점\n"
                                    "   - 고위험 비하 밈(윤두창, 네다홍 등): 80-89점\n"
                                    "   - 중의적 논란어(오조오억, 다케시마 등): 50-75점\n"
                                    "   - 일반 일상어: 30점 미만\n"
                                    "3. **등급 출력**: '등급' 필드에는 반드시 '직접혐오', '사회적밈', '중의적논란', '일상어' 중 하나를 텍스트로만 출력해. 숫자를 절대 쓰지 마.\n"
                                    "4. **판단 근거**: '사과'와 같은 단어는 일상적 사용 빈도가 압도적이므로 오탐 리스크가 매우 높음을 명시해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(텍스트만)\", \"표면적의미\": \"사전적 정의 및 실질 뉘앙스\", \"부정점수\": 0, \"논란의배경\": \"\", \"판단근거\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미 및 실질 뉘앙스:** \n\n {result['표면적의미']}")
                    
                    # 점수가 40점 이상일 때만 경고창 노출 (일상어는 경고 생략 가능)
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
