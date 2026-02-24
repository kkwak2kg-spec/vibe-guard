import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# Secrets 설정 로드
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정 필요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('글로벌 정책 가이드라인에 따라 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 전문가야. 모든 언어에 대해 다음 3단계 점수 체계를 엄격히 적용해.\n\n"
                                    "1. **직접적 욕설/혐오 (90-100점)**: 어떤 맥락에서도 용납되지 않는 명백한 욕설, 인종차별, 성희롱. (예: 씨발, F-word 등)\n"
                                    "   - 정책: 즉시 차단 권고.\n"
                                    "2. **사회적 밈/커뮤니티 비하 (80-90점)**: 특정 커뮤니티에서 파생된 혐오 밈, 고인 모독, 지역 비하. (예: 운지, 흉자 등)\n"
                                    "   - 정책: 커뮤니티 성격에 따라 차단 여부 결정.\n"
                                    "3. **발음 우회/중의적 표현 (60-75점)**: 발음 유사성을 이용한 우회나 일상 용어로 오해받을 수 있는 중의적 단어. (예: 곧휴, 시밤바 등)\n"
                                    "   - 정책: 기계적 차단 지양, 신고 누적 시 검토 권장.\n\n"
                                    "모든 답변은 한국어로 작성하고 temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 위 3단계 체계에 맞춰 JSON으로 분석해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(직접혐오/사회적밈/중의적우회 중 택1)\", \"의미\": \"\", \"부정점수\": 0, \"문화적배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("밸런싱 정책 분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    with st.expander("🌍 상세 분석 및 정책 근거"):
                        st.write(result['문화적배경'])
                        
                    st.info(f"📋 **최종 정책 제안:** \n\n **{result['최종판단']}** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("API 키 설정이 필요합니다.")
