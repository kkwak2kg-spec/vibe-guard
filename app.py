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
                                    "너는 글로벌 게임 서비스의 정책 결정관이야. 다음의 점수 구간을 엄격하게 준수하여 분석해.\n\n"
                                    "1. **직접적 욕설 및 혐오 (90-100점)**: '씨발', '븅신', '병신' 등 예외 없이 공격적인 보편적 욕설. (즉시 차단 권고)\n"
                                    "2. **정치/사회적 비하 밈 (80-89점)**: '윤두창', '이죄명' 등 특정 인물이나 집단을 겨냥한 변형 비하어. (모니터링 및 정책적 판단)\n"
                                    "3. **중의적/커뮤니티 논란어 (50-79점)**: '오조오억', '곧휴' 등 일상 의미와 비하 맥락이 공존하는 단어. (오탐 주의 및 신고 기반 검토)\n\n"
                                    "**주의사항**:\n"
                                    "- '븅신'이나 '씨발'은 정치적 비하가 아니므로 관련 설명을 절대 넣지 마.\n"
                                    "- 실제 인명 가능성이 있는 경우 '0.1%' 같은 표현 대신 전문적인 정책 용어로 서술해.\n"
                                    "- 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"등급\": \"(직접혐오/사회적밈/중의적논란 중 택1)\", \"의미\": \"\", \"부정점수\": 0, \"논란의배경\": \"\", \"최종판단\": \"\", \"운영가이드\": \"\"}}"
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
                        # 90점 이상은 빨간색 강조
                        if result['부정점수'] >= 90:
                            st.metric("분쟁 리스크 점수", f"{result['부정점수']}점", delta="고위험", delta_color="inverse")
                        else:
                            st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    if result['논란의배경']:
                        st.warning(f"⚠️ **상세 맥락:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 가이드라인"):
                        st.write(f"**[판단 근거]**\n{result['최종판단']}")
                        st.write(f"---")
                        st.write(f"**[운영 가이드]**\n{result['운영가이드']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 오류: {inner_e}")
                    
    except Exception as e:
        st.error(f"초기화 오류: {e}")
else:
    st.info("API 키를 설정해 주세요.")
