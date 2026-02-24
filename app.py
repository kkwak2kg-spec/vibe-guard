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
        word_input = st.text_input("분석할 단어:", placeholder="분석할 단어나 문구를 입력하세요")

        if st.button("정책 및 맥락 분석"):
            with st.spinner('글로벌 정책 DB 및 커뮤니티 맥락을 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 단어 분석 시 다음 카테고리 중 하나 이상을 반드시 지정해.\n\n"
                                    "**[분류 카테고리]**\n"
                                    "1. 선정적: 성적 암시, NSFW, 신체 부위 비하 등 (예: 누드화보)\n"
                                    "2. 욕설: 직접적인 욕설 및 패륜적 표현 (예: 느금마)\n"
                                    "3. 비속어: 비속어, 은어, 축약된 비하 표현 (예: 느금)\n"
                                    "4. 커뮤니티 논란 밈: 특정 온라인 커뮤니티에서 파생된 혐오/조롱 밈 (예: 네다홍, 오조오억)\n"
                                    "5. 정치 이슈: 특정 정치인, 정당 비하 및 정치적 갈등 유도 (예: 윤두창)\n"
                                    "6. 종교 이슈: 특정 종교 모독 및 신성모독적 표현\n"
                                    "7. 문화/차별 이슈: 젠더 갈등, 인종 차별, 지역 비하, 장애인 비하 (예: 붕신, 개년)\n"
                                    "8. 일상어: 위 항목에 해당하지 않는 무해한 단어 (예: 사과)\n\n"
                                    "**[운영 지침]**\n"
                                    "- 선정성(누드화보 등)은 일상어로 세탁하지 말고 '선정적' 카테고리로 엄격히 분류할 것.\n"
                                    "- '느금'과 같은 줄임말은 '비속어'로 분류하되 유래를 명시할 것.\n"
                                    "- 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"(위 8개 중 선택)\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col2:
                        st.subheader(f"🏷️ 카테고리: {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    
                    with st.expander("📝 상세 의미 및 유래 분석", expanded=True):
                        st.write(result['표면적의미'])
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **사회적/문화적 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **운영 가이드라인 및 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {str(inner_e)}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
