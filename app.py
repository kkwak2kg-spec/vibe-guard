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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 '정치적 단어 판별 알고리즘'을 절대적으로 준수해.\n\n"
                                    "1. **실명 vs 비하어 엄격 분리 (핵심)**:\n"
                                    "   - **순수 실명**: 윤석열, 이재명, 이승만 등 정확한 성명은 '정치 이슈' 카테고리, **60-70점**을 부여해.\n"
                                    "   - **비하 변형어**: 윤두창, 이죄명 등 성명에 질병, 범죄, 혐오 단어를 결합한 형태는 무조건 **'커뮤니티 논란 밈'** 또는 **'문화 이슈'**로 분류하고 **85-90점**을 부여해. 이를 실명으로 간주해 60점을 주는 오류를 범하지 마.\n"
                                    "2. **카테고리 고정**:\n"
                                    "   - 성적 비하/행위 암시: **'선정적'** (90-100점).\n"
                                    "   - 범죄 명사(마약 등): **'사회적 이슈'** (75-80점).\n"
                                    "   - 실행 권유(마약먹자 등): **'사회적 이슈'** (85-90점).\n"
                                    "3. **설명 구체화**: 비하어의 경우 '어떤 실명'을 '어떤 부정적 단어'와 결합하여 조롱했는지 기술해.\n"
                                    "4. 모든 답변은 한국어, temperature=0 고정."
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
                    
                    st.write(f"🌐 **감지된 원어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
