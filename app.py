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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 점수 및 카테고리 가이드를 절대적으로 준수해.\n\n"
                                    "1. **점수 상한선 강제 준수**:\n"
                                    "   - 단순 범죄/불법 명사 (예: 마약, 대포통장): **75-80점** 고정. 절대 90점을 넘기지 마.\n"
                                    "   - 범죄 실행 권유 (예: 마약먹자, 판매함): **85-90점**.\n"
                                    "   - 직접적 욕설/선정적 비하 (예: 보빨, 씨발): **90-100점**.\n"
                                    "   - 정치인 실명: **60-70점** 고정.\n"
                                    "2. **카테고리 매칭 로직**:\n"
                                    "   - 성적 행위/신체 비하 맥락이 있으면 무조건 **'선정적'**.\n"
                                    "   - 불법 행위/범죄 관련은 무조건 **'사회적 이슈'**.\n"
                                    "   - 인종/지역/역사 비하는 **'문화 이슈'**.\n"
                                    "3. **맥락 전이 금지**: 단어 '마약' 분석 시 '선정적 카테고리가 아니다'라는 식의 타 카테고리 언급을 일절 금지해. 오직 해당 단어의 범죄 리스크만 분석해.\n"
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
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
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
