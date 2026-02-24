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
                                    "너는 글로벌 게임 정책 결정관이자 정치/사회학 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **정치적 비하 밈 탐지**: '이죄명', '윤두창' 등 정치인의 실명을 변형하여 범죄나 부정적 이미지에 결합한 단어는 단순 인명이 아님. 반드시 **'정치 이슈'** 또는 **'커뮤니티 논란 밈'**으로 분류하고 85-90점의 고득점을 부여해.\n"
                                    "2. **인명과 비하어 구분**: '이재명'과 같은 실명(70점 미만)과 '이죄명'과 같은 조롱 표현(85점 이상)의 점수 차이를 명확히 해. 조롱 표현은 유저 간 분쟁을 직접적으로 유도함.\n"
                                    "3. **변형 수법 상세 분석**: '죄'와 같이 특정 단어를 삽입하여 비하 의도를 드러낸 수법을 '표면적 의미' 섹션에 기술해.\n"
                                    "4. **성적 맥락 금지**: 성적 의미가 없는 정치 비하어에 성적 비하를 언급하지 마.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 85~90, \"표면적의미\": \"비하를 위한 변형 수법 분석\", \"논란의배경\": \"특정 정치인에 대한 조롱 및 갈등 맥락\", \"판단근거\": \"분쟁 유발 리스크에 따른 제재 권고\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col_score, col_cat = st.columns(2)
                    with col_score:
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미 및 변형 분석:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
