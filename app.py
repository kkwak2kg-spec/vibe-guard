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
                                    "너는 글로벌 게임 정책 결정관이야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **등급 출력 오류 방지**: '등급' 필드에는 반드시 '직접혐오', '사회적밈', '중의적논란' 중 하나를 텍스트로만 써. 절대로 '90-100' 같은 숫자를 쓰지 마.\n"
                                    "2. **합리적 점수 조정**: '네다홍', '다케시마'처럼 특정 국가/지역의 명칭이거나 중의적 해석 여지가 있는 단어는 무조건 95점을 주기보다, 갈등 유발 가능성을 고려해 80-88점 사이로 밸런싱해.\n"
                                    "3. **이중 맥락 서술**: '다케시마'는 일본의 독도 명칭이라는 사실적 측면과 한국 내 역사적 반발 맥락을 대조해 서술하고, '네다홍'은 색상 용어 가능성과 지역 비하 밈을 대조해.\n"
                                    "4. **전문적 판단**: 실제 사용 사례가 단순 지칭인지 비하 의도인지에 따라 오탐 가능성을 '판단 근거'에 포함해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(텍스트만)\", \"표면적의미\": \"\", \"부정점수\": 80~90, \"논란의배경\": \"\", \"판단근거\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        # 숫자가 아닌 텍스트 등급이 나오도록 강제
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미 및 실질 뉘앙스:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 50:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
