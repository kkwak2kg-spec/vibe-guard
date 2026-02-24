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
                                    "너는 글로벌 게임 정책 결정관이자 한국 근현대사/커뮤니티 전문가야. "
                                    "아래 지침을 기계적으로 준수하여 구체적인 보고서를 작성해.\n\n"
                                    
                                    "1. **위장 혐오 표현의 본질 분석**: '피떡갈비', '통구이' 등 음식명으로 위장한 단어 분석 시, 단순히 '음식 비하'라고 하지 마. "
                                    "이 단어들이 **'특정 역사적 사건 희생자들의 참혹한 모습'**을 음식에 빗대어 조롱하는 **고인 모독 및 반인륜적 잔혹성**을 담고 있음을 명확히 기술해.\n"
                                    
                                    "2. **구체적 맥락 기술**: 어떤 지역, 어떤 역사적 사건의 희생자를 타겟으로 하는지, 왜 이 단어가 사회적으로 극심한 혐오감을 유발하는지 상세히 분석해.\n"
                                    
                                    "3. **카테고리 및 점수 가이드**:\n"
                                    "   - 위장 잔혹 비하어: 반드시 **80-88점** 및 **'문화 이슈'** 또는 **'커뮤니티 논란 밈'**.\n"
                                    "   - 욕설/선정적: 반드시 **90-100점**.\n"
                                    "   - 사회적 이슈(범죄): **75-80점**.\n"
                                    "   - 정치 이슈(실명): **60-70점**.\n"
                                    "   - 일상어: **10-20점**.\n\n"
                                    
                                    "4. **환각 방지**: 언어 필드에 단어명(예: 마약) 복사 금지, 카테고리에 점수 범위 표기 금지."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"한국어\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"사전적 정의\", \"논란의배경\": \"역사적/사회적 배경 및 잔혹성 상세 분석\", \"판단근거\": \"운영 정책상 리스크 관리 가이드\"}}"
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
                        st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    else:
                        st.info(f"💡 **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
