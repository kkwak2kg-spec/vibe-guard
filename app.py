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
        
        # 입력창의 예시(placeholder)를 빈칸("")으로 수정했습니다.
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('해당 단어의 커뮤니티 맥락과 중의성을 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 및 한국 온라인 커뮤니티 문화 전문가야.\n"
                                    "1. **커뮤니티 분쟁 용어 분석**: '흉자', '한남', '메갈' 등 특정 성별 혐오나 커뮤니티 갈등에서 비롯된 신조어를 정확히 분석해. "
                                    "단순한 사전적 의미가 아니라 실제 온라인 상에서 상대방을 비하하거나 낙인찍는 용도로 쓰이는 맥락을 우선시해.\n"
                                    "2. **중의성 및 오탐 방지**: 단어에 학술적 의미나 인명 등의 중의성이 있다면 이를 반드시 언급하고 점수에 반영해.\n"
                                    "3. **일관성**: 비하 의도가 명확한 커뮤니티 용어는 70-85점 사이의 '주의' 혹은 '차단' 판정을 내려.\n"
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
