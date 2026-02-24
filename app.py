import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# --- API 키 로드 로직 ---
api_key = None

# 1. Streamlit Secrets 확인
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
# 2. 만약 Secrets에 없다면 사이드바에서 입력 받기 (백업용)
else:
    api_key = st.sidebar.text_input("API Key가 Secrets에 설정되지 않았습니다. 직접 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="예: 시밤바, 새끼, 애자")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('정밀 분석 중...'):
                try:
                    # '시밤바' 오판독 방지 및 한국어 고정을 위한 강력한 지침
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 전문가야. 모든 필드의 내용은 반드시 한국어로 작성해.\n"
                                    "1. '시밤바'와 같은 변형 표현은 원본 욕설보다 낮은 60-70점대로 부여하고, '성적 의미'로 오독하지 마.\n"
                                    "2. '새끼'는 신체 비하가 아닌 단순 비속어/욕설로 분류해.\n"
                                    "3. temperature=0으로 고정하여 일관된 점수를 유지해."
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
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    st.info(f"📋 **가이드:** {result['최종판단']}\n\n{result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    # 상세 에러 메시지 출력 (디버깅용)
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.warning("API 키가 필요합니다. Streamlit Secrets 설정을 확인하거나 사이드바에 입력해 주세요.")
