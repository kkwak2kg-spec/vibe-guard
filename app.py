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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 한국어 비속어 어원 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **어원 분석의 정확성**: '느검마'와 같은 단어를 '느끼한+검은' 등으로 잘못 해석하지 마. "
                                    "이 단어는 '너의 엄마'를 비하하는 패륜적 욕설임을 명확히 밝혀. 억측이나 창의적인 합성어 해석을 절대 금지해.\n"
                                    "2. **카테고리 분류**: 선정적 / 욕설 / 비속어 / 커뮤니티 논란 밈 / 정치 이슈 / 종교 이슈 / 문화 이슈 / 일상어 중 하나를 선택해.\n"
                                    "3. **점수 하한선**: 명백한 패륜 욕설은 95-100점을 부여해.\n"
                                    "4. **판단 근거**: 단어의 실제 의미가 유저에게 줄 수 있는 심리적 타격과 운영 리스크를 중심으로 기술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 95~100, \"표면적의미\": \"실제 어원과 비하 대상을 구체적으로 기술\", \"논란의배경\": \"가족 비하 및 패륜적 맥락 상세히\", \"판단근거\": \"정책적 사유 및 대응 권고\"}}"
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
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미 및 유래:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
