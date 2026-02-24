import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# Secrets 설정 확인 (대문자 일치 필수)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key가 설정되지 않았습니다. 직접 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="예: 운지, 애자, 시밤바")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('한국 특유의 사회적 혐오 맥락을 정밀 추적 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 전문가이자 한국 온라인 혐오 표현 및 밈(Meme) 분석 전문가야.\n"
                                    "1. **한국 고유 혐오 맥락**: '운지'와 같이 특정 커뮤니티에서 고인을 모독하거나 비하하려는 목적으로 파생된 단어들을 반드시 짚어내야 해. "
                                    "단순히 사전적 의미(예: 운전, 떨어짐)로 해석하지 말고, 실제 온라인상의 부정적 사용 사례를 우선해.\n"
                                    "2. **유형 분류**: 단순 비속어, 고인 모독, 지역 비하, 신체 비하 등을 엄격히 구분해.\n"
                                    "3. **점수 하한선**: 고인 비하 및 혐오 표현은 명백한 차단 대상이므로 최소 90점 이상을 부여해.\n"
                                    "4. 모든 답변은 한국어로 작성하고 temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 한국의 온라인 커뮤니티 맥락에서 분석해서 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"유형\": \"\", \"의미\": \"\", \"부정점수\": 0, \"문화적배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("정밀 분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        # 90점 이상은 빨간색으로 경고
                        if result['부정점수'] >= 90:
                            st.error(f"📍 최종 판단: {result['최종판단']}")
                        else:
                            st.warning(f"📍 최종 판단: {result['최종판단']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    with st.expander("🌍 상세 분석 및 역사적 배경"):
                        st.write(result['문화적배경'])
                        
                    st.info(f"📋 **정책 가이드라인:** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.warning("API 키 설정이 필요합니다.")
