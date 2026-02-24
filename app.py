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
                                    "너는 글로벌 게임 정책 결정관이자 한국 근현대사/온라인 커뮤니티 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **위장 혐오 표현 탐지**: '피떡갈비', '홍어', '통구이' 등 음식 이름으로 위장했으나 실제로는 특정 지역 비하, 역사적 사건 희생자 조롱, 고인 모독을 목적으로 하는 단어를 절대 놓치지 마. 이를 '일상어'로 분류하는 것은 치명적인 운영 오류임.\n"
                                    "2. **잔혹성 가점**: 희생자의 모습이나 신체를 음식에 비유하는 잔혹한 비하 표현은 예외 없이 100점을 부여하고 '문화 이슈' 혹은 '커뮤니티 논란 밈'으로 분류해.\n"
                                    "3. **카테고리 우선순위**: \n"
                                    "   - 보편적 욕설(씨발 등): '욕설'\n"
                                    "   - 성적 비하/대상화: '선정적'\n"
                                    "   - 인물 실명: '정치 이슈' (비하 변형 없을 시 60-70점)\n"
                                    "   - 특정 집단/역사 비하 밈: '문화 이슈' 또는 '커뮤니티 논란 밈'\n"
                                    "4. **할루시네이션 방지**: 단어의 표면적 정의에 매몰되지 말고, 한국 온라인 커뮤니티에서 실제로 사용되는 혐오적 뉘앙스를 최우선으로 분석해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 100, \"표면적의미\": \"\", \"논란의배경\": \"숨겨진 혐오/비하 및 역사적 맥락 상세히\", \"판단근거\": \"\"}}"
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
                    st.info(f"📖 **표면적 의미 및 분석:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
