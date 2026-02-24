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
            with st.spinner('단어의 다각적 맥락을 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 언어학 및 커뮤니티 정책 전문가야.\n"
                                    "1. **중의적 맥락 노출**: '오조오억'이나 '허버허버'처럼 단어 자체는 비속어가 아니더라도, 특정 온라인 커뮤니티에서 젠더 갈등이나 정치적 비하 목적으로 사용되는 '숨은 배경'이 있다면 이를 상세히 리포트해.\n"
                                    "2. **점수 밸런싱**: 단어 자체에 욕설이 없다면 점수를 무리하게 높이지 마(60-70점대 유지). 대신 운영자가 '왜 논란이 되는지'를 캐치할 수 있게 분석 사유를 강화해.\n"
                                    "3. **카테고리 분류**: 직접 욕설이 아닌 경우 '중의적 우회' 혹은 '커뮤니티 논란어'로 분류해.\n"
                                    "4. 모든 답변은 한국어, temperature=0."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해줘. 특히 일상적 의미와 커뮤니티 논란 배경을 구분해서 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"의미\": \"사전적 의미\", \"부정점수\": 0, \"논란의배경\": \"커뮤니티 내 갈등 요소 및 유래\", \"최종판단\": \"운영자 가이드\", \"운영가이드라인\": \"구체적 대응 팁\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("맥락 기반 분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **사전적 의미:** {result['의미']}")
                    
                    # 논란의 배경 섹션을 시각적으로 강조
                    st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 상세 가이드"):
                        st.write(f"**판단 근거:** {result['최종판단']}")
                        st.write(f"**실무 팁:** {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("API 키 설정이 필요합니다.")
