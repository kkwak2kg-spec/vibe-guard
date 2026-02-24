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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 '점수 범위 강제 지침'을 절대적으로 준수해.\n\n"
                                    "1. **카테고리별 점수 하한선/상한선 고정 (필수)**:\n"
                                    "   - **욕설/비속어**: 반드시 **90-100점** 사이로 책정해. '씨발' 등은 10점이 될 수 없음.\n"
                                    "   - **선정적**: 반드시 **90-100점** 사이로 책정해.\n"
                                    "   - **커뮤니티 논란 밈/비하어**: '윤두창' 등은 **85-90점**.\n"
                                    "   - **사회적 이슈 (범죄)**: '마약' 등은 **75-80점**.\n"
                                    "   - **정치 이슈 (실명)**: '이승만', '윤석열' 등은 **60-70점**.\n"
                                    "   - **일상어**: '가즈아' 등 긍정적 표현만 **10-20점**.\n"
                                    "2. **설명 일관성**: 욕설 분석 시 일상어나 정치적 맥락을 언급하지 마. 오직 해당 단어의 폭력성만 설명해.\n"
                                    "3. 모든 답변은 한국어, temperature=0 고정."
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
                        # 욕설일 경우 강제로 고득점이 나오도록 로직 감시
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 원어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
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
