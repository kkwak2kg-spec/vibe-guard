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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 단어 분석 시 다음 기준을 적용해.\n\n"
                                    "1. **이중 맥락 분석**: 단어가 'AlZubair'처럼 특정 문화권의 이름이나 사전적 의미를 가진 경우, 비하적 맥락을 분석하기 전에 반드시 그 '표면적/원래 의미'를 먼저 명시해.\n"
                                    "2. **점수 및 등급**: 명백한 욕설은 90점 이상, 정치/사회적 밈은 80-89점, 중의적 우회 및 논란어는 50-79점을 부여해.\n"
                                    "3. **전문적 판단**: '0.1% 확률' 같은 비전문적 표현 대신 '인명 사용 가능성' 등 정책 용어를 사용해.\n"
                                    "4. **항목 구성**: '표면적 의미'와 '논란의 배경'을 명확히 구분하여 운영자가 오탐 가능성을 즉시 파악하게 해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"표면적의미\": \"단어의 원래 사전적/인명적 의미\", \"부정점수\": 0, \"논란의배경\": \"사회적/정치적/커뮤니티 비하 맥락\", \"판단근거\": \"전문적 정책 논리\", \"운영가이드\": \"단계별 대응 지침\"}}"
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
                    # 사용자님 제안 반영: 표면적 의미를 상단에 강조
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 50:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 가이드라인"):
                        st.write(f"**[판단 근거]**\n{result['판단근거']}")
                        st.write(f"---")
                        st.write(f"**[운영 가이드]**\n{result['운영가이드']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
