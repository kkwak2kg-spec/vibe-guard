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
                                    "너는 글로벌 게임 서비스의 정책 결정관이야. 다음의 전문적 분석 기준을 엄격히 적용해.\n\n"
                                    "1. **점수 및 등급**: 정치인 비하 용어는 분쟁 유발 가능성을 고려하여 80-85점을 부여하고 '사회적밈'으로 분류해.\n"
                                    "2. **객관적 서술**: '0.1% 확률'과 같은 비전문적 수치 표현을 절대 사용하지 마. 대신 '실제 인명으로 사용될 가능성을 배제할 수 없으므로', '맥락에 따른 오탐 가능성이 존재함'과 같이 전문적인 용어로 서술해.\n"
                                    "3. **항목 명칭**: 최종 결과에서 '실무 대응 팁' 대신 '운영 가이드'라는 명칭을 사용해.\n"
                                    "4. **구체적 맥락**: 정치적 비하 표현의 경우 대상과 비하 방식(예: 성과 비속어 합성 등)을 명확히 기술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"의미\": \"어원 및 비하 대상 명시\", \"부정점수\": 80~85, \"논란의배경\": \"정치적/사회적 갈등 맥락\", \"최종판단\": \"전문적인 용어를 사용한 판단 근거\", \"운영가이드\": \"운영팀을 위한 단계별 대응 지침\"}}"
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
                    
                    with st.expander("🌍 운영 정책 가이드라인"):
                        st.write(f"**[판단 근거]**\n{result['최종판단']}")
                        st.write(f"---")
                        st.write(f"**[운영 가이드]**\n{result['운영가이드']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("API 키를 설정해 주세요.")
