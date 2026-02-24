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
        word_input = st.text_input("분석할 단어:", placeholder="예: 운지, 애자, 시밤바")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('단어의 중의성과 사회적 맥락을 동시에 검토 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 수석 정책 결정관이야. 균형 잡힌 판단을 위해 다음 기준을 따라.\n"
                                    "1. **중의성 판단**: '운지'나 '애자'처럼 특정 커뮤니티의 혐오 표현이면서도 동시에 학술적 의미(운지: 손가락 법)나 인명, 일상적 의미가 존재하는 경우 이를 반드시 언급해.\n"
                                    "2. **유연한 점수제**: 명백한 욕설은 90점 이상으로 유지하되, 중의성이 있어 선량한 유저가 피해를 볼 가능성이 있다면 70-80점대로 조정하고 '주의' 판정을 내려.\n"
                                    "3. **오탐 방지 가이드**: 시스템 차단 시 발생할 수 있는 부작용(예: 특정 연주자의 대화 차단 등)을 '최종판단'에 포함해.\n"
                                    "4. 모든 답변은 한국어, temperature=0."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'의 다각적 분석 JSON: {{\"언어\": \"\", \"유형\": \"\", \"의미\": \"사전적/중의적 의미 포함\", \"부정점수\": 0, \"문화적배경\": \"비하적 맥락 설명\", \"최종판단\": \"차단 여부 및 오탐 주의사항\", \"운영가이드라인\": \"실제 운영 적용 팁\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("균형 분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **최종 판단:** {result['최종판단']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    with st.expander("🌍 상세 분석 및 문화적 배경"):
                        st.write(result['문화적배경'])
                        
                    st.info(f"📋 **운영 가이드라인:** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("API 키 설정이 필요합니다.")
