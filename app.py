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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 한국 온라인 커뮤니티 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **한국어 지역 비하/혐오 표현 강화**: '네다홍', '절라계', '통구이' 등 특정 지역을 비하하거나 고인 모독과 관련된 혐오 표현은 색상이나 일상 용어로 세탁된 의미가 있더라도 게임 내에서는 90점 이상의 최고 위험도로 분류해.\n"
                                    "2. **실질적 뉘앙스 상세화**: '네다홍'과 같은 단어는 색상 조합이 아닌, 특정 지역 유저를 조롱하고 배척하기 위한 극단적인 비하 표현임을 명확히 밝혀.\n"
                                    "3. **점수 및 등급**: 명백한 지역 비하 및 혐오 밈은 '사회적밈' 혹은 '직접혐오'로 분류하고 90-100점을 부여해.\n"
                                    "4. **표면적 의미와 논란 대조**: 겉으로 무해해 보이는 단어가 어떻게 혐오 표현으로 변질되었는지 그 유래와 실질적 공격성을 구체적으로 기술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"표면적의미\": \"단어의 표면적 의미와 실제 구어체 실질 뉘앙스\", \"부정점수\": 0, \"논란의배경\": \"커뮤니티 내 비하 유래 및 혐오 맥락\", \"판단근거\": \"정책적 사유 및 유저 분쟁 리스크 분석\"}}"
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
                    
                    if result['부정점수'] >= 50:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
