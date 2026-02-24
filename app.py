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
                                    "1. **정치인 성명 처리**: 정치인의 실명(예: 이재명, 윤석열 등)은 비속어가 아니므로 '비속어' 카테고리로 분류하지 마. 반드시 **'정치 이슈'**로 분류해.\n"
                                    "2. **합리적 점수 부여**: 단순 정치인 성명은 95점과 같은 고득점을 주지 마. 분쟁 유발 가능성을 고려하되 60-70점 사이의 중립적 점수를 부여해.\n"
                                    "3. **불필요한 성적 맥락 언급 금지**: 성적인 의미가 전혀 없는 단어에 대해 '성적 비하와 무관하다'는 식의 부정형 설명을 반복하지 마. 오직 해당 단어의 실제 정치적/사회적 맥락만 설명해.\n"
                                    "4. **언어 및 어원**: 외국어 비속어(예: chinorri)의 경우 한국어로 오인하지 말고 실제 언어(스페인어 등)를 정확히 감지해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"(정치 이슈/문화 이슈/선정적/욕설/비속어/사회적 이슈/일상어 중 선택)\", \"부정점수\": 60~75, \"표면적의미\": \"실제 인물 정보 또는 사전적 정의\", \"논란의배경\": \"정치적/사회적 갈등 맥락 상세히\", \"판단근거\": \"운영 정책상 관리 방안\"}}"
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
