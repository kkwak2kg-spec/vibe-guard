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
                                    "너는 글로벌 게임 정책 결정관이자 다국어 분석 전문가야. 아래 지침을 기계적으로 준수해.\n\n"
                                    "1. **언어 감지 정규화 (필수)**: '언어' 필드에는 반드시 실제 언어 명칭(예: 한국어, 영어, 스페인어 등)만 써. 단어 '마약'을 분석한다고 해서 언어를 '마약'이라고 쓰는 오류를 절대 범하지 마.\n"
                                    "2. **카테고리별 점수 격리**:\n"
                                    "   - 욕설/선정적 (씨발, 보빨 등): **90-100점**.\n"
                                    "   - 비하 밈/문화 이슈 (윤두창, 오조오억 등): **80-88점**.\n"
                                    "   - 불법/사회적 이슈 (마약 등): **75-80점**.\n"
                                    "   - 정치인 실명: **60-70점**.\n"
                                    "   - 일상어 (가즈아 등): **10-20점**.\n"
                                    "3. **맥락 전이 차단**: 분석 중인 단어와 상관없는 타 카테고리의 방어 논리(예: 부당한 정치적 연결 시도 등)를 재활용하지 마.\n"
                                    "4. 모든 답변은 한국어 표준 명칭 사용, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"반드시 '한국어' 또는 해당 원어 명칭 기재\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
                    
                    # 언어 필드가 단어와 동일하게 나오지 않도록 검증 레이어 추가
                    detected_lang = result['언어'] if result['언어'] != word_input else "한국어(추정)"
                    st.write(f"🌐 **감지된 언어:** {detected_lang}")
                    
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
