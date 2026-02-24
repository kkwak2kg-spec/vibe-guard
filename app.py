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
                                    "너는 글로벌 게임 서비스의 정책 결정관이야. 다음의 정교한 점수 체계를 적용해.\n\n"
                                    "1. **카테고리 구분**: 선정적 / 욕설 / 비속어 / 커뮤니티 논란 밈 / 정치 이슈 / 종교 이슈 / 사회적 이슈 / 문화 이슈 / 일상어 중 선택.\n"
                                    "2. **합리적 점수 밸런싱**:\n"
                                    "   - 직접적 욕설/패륜/선정적 강요: 95-100점\n"
                                    "   - 사회적 이슈(범죄 명칭 등): 70-80점 (단어 자체는 표준어이나 범죄 맥락이 큰 경우)\n"
                                    "   - 커뮤니티 비하 밈: 80-89점\n"
                                    "   - 일상어: 30점 미만 (절대 고득점 금지)\n"
                                    "3. **대포통장 특수 지침**: '사회적 이슈'로 분류하되, 뉴스에서도 쓰이는 용어임을 감안해 70-80점을 부여하고, 단어의 유해성보다 범죄 이용 리스크를 강조해.\n"
                                    "4. **등급 및 문구**: 등급은 텍스트로만 출력하고, 모든 정책 사유는 '판단근거'에 통합해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
                        st.warning(f"⚠️ **사회적/문화적 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
