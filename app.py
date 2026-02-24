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
            # 요청하신 대로 간소화된 문구 적용
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 정책 결정관이야. 다음의 밸런싱 기준을 엄격히 적용해.\n\n"
                                    "1. **점수 하이라이트**: 정치인 비하 용어(예: 윤두창 등)는 분쟁 유발 가능성이 매우 높으므로 80-85점을 부여해. "
                                    "단, 실제 인명으로 사용될 가능성이 0.1%라도 있다면 이를 반드시 '최종판단'에 명시해.\n"
                                    "2. **구체적 어원 분석**: '현직 대통령의 성과 특정 질병/비속어를 합성한 표현'임을 명확히 밝혀.\n"
                                    "3. **등급 분류**: 명백한 욕설은 '직접혐오'이나, 인명 가능성이 있는 정치 밈은 '사회적밈' 혹은 '커뮤니티논란어'로 분류해.\n"
                                    "4. 모든 답변은 한국어, temperature=0."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"의미\": \"어원 및 대상 구체적 명시\", \"부정점수\": 80~85, \"논란의배경\": \"정치적/사회적 갈등 맥락\", \"최종판단\": \"인명 가능성 및 오탐 주의사항 포함\", \"운영가이드라인\": \"운영팀 대응 팁\"}}"
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
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 상세 가이드"):
                        st.write(f"**판단 근거:** {result['최종판단']}")
                        st.write(f"**실무 대응 팁:** {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("API 키를 설정해 주세요.")
