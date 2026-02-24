import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="예: 새끼, 씨발, 애자")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('정확한 어원과 카테고리를 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 및 언어학 전문가야. 단어 분석 시 다음 가이드를 엄격히 따라.\n"
                                    "1. **카테고리 정확성**: 비속어의 유형을 명확히 구분해. (예: '새끼'는 단순 비속어/욕설이지 신체 비하가 아님)\n"
                                    "2. **어원 중심 분석**: 단어의 실제 유래를 바탕으로 의미를 설명해. 근거 없는 '신체 비하' 판정을 금지해.\n"
                                    "3. **점수 체계**: \n"
                                    "   - 95-100점: 반사회적 혐오, 범죄, 극도의 패륜.\n"
                                    "   - 85-94점: 강한 욕설 (씨발 등).\n"
                                    "   - 60-84점: 비하어(신체, 특정집단) 및 일반 비속어(새끼 등).\n"
                                    "4. 모든 답변은 한국어로 작성하고 temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 아래 한글 키의 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"유형\": \"(예: 단순 비속어, 신체 비하, 인종 차별 등)\", \"의미\": \"\", \"부정점수\": 0, \"문화적배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
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
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분류:** {result['유형']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    with st.expander("🌍 상세 분석 및 배경"):
                        st.write(result['문화적배경'])
                        
                    st.info(f"📋 **정책 가이드라인:** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error("분석 중 오류가 발생했습니다.")
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력해 주세요.")
