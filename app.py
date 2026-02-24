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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 단어 분석 시 다음 기준을 엄격히 적용해.\n\n"
                                    "1. **단어 유래의 명확성**: '느금'과 같이 특정 욕설의 줄임말로 추정되는 단어는 '느금마(너희 어머니)의 줄임말로 사용될 가능성이 높음'과 같이 그 기원을 구체적으로 명시해.\n"
                                    "2. **형태적 모호함 지적**: 단어 자체가 완전한 욕설 형태가 아닐 경우 '표현이 명확하지 않으므로 사용 맥락을 주의하여 판단할 필요가 있음'이라는 가이드를 반드시 포함해.\n"
                                    "3. **일상어 보호 및 점수 밸런싱**: '사과' 같은 일상어는 30점 미만, '느금'처럼 비하 의도가 강하나 형태가 축약된 단어는 70-80점, 명백한 욕설은 90점 이상을 부여해.\n"
                                    "4. **등급 출력**: '등급' 필드에는 '직접혐오', '사회적밈', '중의적논란', '일상어' 중 하나를 반드시 텍스트로만 출력해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(텍스트만)\", \"표면적의미\": \"사전적 정의 및 구체적 유래(줄임말 여부 등)\", \"부정점수\": 0, \"논란의배경\": \"커뮤니티 내 비하 맥락 및 실제 사용 사례\", \"판단근거\": \"정책적 사유 및 형태적 모호성에 따른 주의사항\"}}"
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
                    st.info(f"📖 **표면적 의미 및 유래:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
