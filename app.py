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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 '일상어 보호 및 오탐 방지 지침'을 절대적으로 준수해.\n\n"
                                    "1. **일상어 및 격려 표현 보호**: '가즈아'와 같은 긍정적 격려, 응원, 투자 커뮤니티 유행어는 비하 발언이 아님. 반드시 **'일상어'**로 분류하고 점수는 **10-20점** 수준으로 낮게 책정해.\n"
                                    "2. **정치적 맥락 끼워맞추기 금지**: 일반적인 단어를 특정 정치인이나 사건과 억지로 연결하여 비하 의도가 있다고 소설을 쓰지 마(할루시네이션 방지). 명백한 비하 변형어(예: 윤두창, 이죄명)일 때만 정치 이슈로 다뤄.\n"
                                    "3. **카테고리 정밀화**:\n"
                                    "   - 성적 비하/행위: **'선정적'** (90-100점).\n"
                                    "   - 범죄 관련: **'사회적 이슈'** (75-80점).\n"
                                    "   - 정치적 비하 변형어: **'커뮤니티 논란 밈'** (85-90점).\n"
                                    "4. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"부당한 정치적 연결 시도 금지 및 실제 유래 기술\", \"판단근거\": \"\"}}"
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
                    
                    # 일상어일 경우 경고(warning) 대신 안내(info) 메시지 출력 고려
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    else:
                        st.info(f"💡 **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
