import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 1. API 키 자동 로드 (Secrets 사용)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key가 설정되지 않았습니다. 직접 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="예: 시밤바, 새끼, 애자")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('언어학적 맥락을 정밀 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 및 언어학 전문가야.\n"
                                    "1. **변형 욕설 주의**: '시밤바'처럼 실제 욕설을 희화화하거나 변형한 단어는 원본 욕설보다는 낮은 점수(60-70점)를 부여하고, '완곡한 비속어'로 분류해.\n"
                                    "2. **성적 의미 남용 금지**: 명백한 성적 어원이 없는 경우 성적인 의미가 있다고 단정하지 마.\n"
                                    "3. **정확한 유형 분류**: 단순 비속어, 신체 비하, 혐오 표현 등을 엄격히 구분해.\n"
                                    "4. 모든 답변은 한국어, temperature=0."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"유형\": \"\", \"의미\": \"\", \"부정점수\": 0, \"문화적배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
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
                    
                    st.write(f"📖 **의미:** {result['의미']}")
                    st.info(f"📋 **정책 가이드:** {result['최종판단']}\n\n{result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error("분석 중 오류가 발생했습니다.")
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("API 키가 필요합니다.")
