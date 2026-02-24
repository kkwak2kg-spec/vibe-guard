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
                    # [구조 개선] AI에게 판단을 맡기지 말고, 각 단어의 성격을 명확히 규정
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 금칙어 정책 마스터야. 아래 '카테고리별 출력 규정'을 기계적으로 준수해.\n\n"
                                    "1. **카테고리명 고정**: 절대로 'Protocol D'나 'D' 같은 내부 명칭을 출력하지 마. 오직 다음 중 하나만 선택해: [욕설/비속어, 선정적, 정치 이슈, 문화 이슈, 사회적 이슈, 커뮤니티 논란 밈, 일상어]\n\n"
                                    "2. **점수 하한선 강제 가이드 (중요)**:\n"
                                    "   - 욕설/선정적 (씨발, 보빨 등): 반드시 90-100점.\n"
                                    "   - 비하 밈 (윤두창, 이죄명 등): 반드시 85-90점.\n"
                                    "   - 젠더 갈등 밈 (오조오억 등): 10점이 아님. 사회적 갈등 유발성을 고려해 80-85점으로 분류하고 카테고리는 '문화 이슈'로 고정해.\n"
                                    "   - 불법/범죄 (마약 등): 75-80점.\n"
                                    "   - 정치인 실명 (윤석열 등): 60-70점.\n"
                                    "   - 순수 응원/일상어 (가즈아 등): 10-20점.\n\n"
                                    "3. 모든 설명에서 이전 대화의 방어 논리를 재활용하지 마. 단어 고유의 맥락만 분석해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
