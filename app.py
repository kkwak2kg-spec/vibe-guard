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
                                    "너는 글로벌 게임 정책 결정관이자 인권/사회학 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **카테고리 세분화 및 정확성**: \n"
                                    "   - **문화 이슈**: 인종 차별(예: nigga), 젠더 갈등(예: 개년), 지역 비하(예: 네다홍), 신체/장애 비하 등 특정 집단에 대한 혐오가 담긴 표현은 반드시 '문화 이슈'로 분류해. 이를 단순 욕설로 퉁치지 마.\n"
                                    "   - **선정적**: 성적 행위/대상화 관련 표현.\n"
                                    "   - **사회적 이슈**: 범죄, 불법 거래(예: 대포통장) 관련 표준어.\n"
                                    "   - **욕설/비속어**: 직접적 패륜 욕설이나 보편적 비속어.\n"
                                    "2. **글로벌 인지력**: 한국어뿐만 아니라 영미권, 동남아시아권 욕설의 실제 어원(예: Bapakkau=인도네시아어 아버지 비하)을 정확히 파악해.\n"
                                    "3. **할루시네이션 방지**: '자지털'을 '자산+디지털'로 해석하는 식의 억지 미화를 절대 금지해.\n"
                                    "4. **점수 및 등급**: 문화적 혐오와 차별 표현은 글로벌 서비스 시 가장 리스크가 크므로 95-100점을 부여해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"(문화 이슈/선정적/욕설/비속어/정치 이슈/사회적 이슈/일상어 중 선택)\", \"부정점수\": 95~100, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
