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
        
        # 입력창 placeholder는 빈칸으로 유지
        word_input = st.text_input("분석할 단어:", placeholder="")

        # 버튼 명칭을 '분석'으로 간소화했습니다.
        if st.button("분석"):
            with st.spinner('다각적 맥락 및 정책 가이드를 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 및 커뮤니티 전문가야. 다음 기준을 엄격히 지켜.\n\n"
                                    "1. **점수 하한선 설정**: '오조오억', '허버허버'와 같이 단어 자체는 비속어가 아니더라도 커뮤니티 분쟁 소지가 있는 단어는 0점이 아닌 50-60점을 부여해.\n"
                                    "2. **등급 출력 오류 수정**: '등급' 필드에는 숫자가 아닌 반드시 '직접혐오', '사회적밈', '중의적우회', '커뮤니티논란어' 중 하나의 텍스트를 출력해.\n"
                                    "3. **운영적 관점**: 단어의 의미뿐만 아니라 해당 단어가 채팅창에 노출되었을 때 발생할 수 있는 유저 간의 갈등 가능성을 '운영가이드라인'에 상세히 적어.\n"
                                    "4. 모든 답변은 한국어, temperature=0."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(텍스트로 출력)\", \"의미\": \"사전적 의미\", \"부정점수\": 50~100, \"논란의배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("맥락 기반 정책 분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        # 0점이 나오지 않도록 보정된 점수 출력
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        # 숫자가 아닌 텍스트 등급 출력 확인
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **사전적 의미:** {result['의미']}")
                    
                    # 커뮤니티 논란 배경 노출
                    st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 상세 가이드"):
                        st.write(f"**판단 근거:** {result['최종판단']}")
                        st.write(f"**실무 대응 팁:** {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("API 키 설정이 필요합니다.")
