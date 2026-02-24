import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="예: 씨발, 애자, 卍")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('최고 수준의 보안 기준으로 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 수석 정책 결정관이야. 점수 산정 시 다음의 엄격한 기준을 적용해.\n"
                                    "1. **90-100점 (필수 차단)**: 명백한 욕설(씨발 등), 패륜적 발언, 인종차별, 성희롱, 혐오 표현. 예외 없이 90점 이상 부여.\n"
                                    "2. **70-89점 (강력 주의)**: '애자'와 같은 신체 비하 단어, 심한 모욕감을 줄 수 있는 신조어.\n"
                                    "3. **50-69점 (주의/모니터링)**: 중의적 표현이나 상황에 따라 공격적일 수 있는 단어.\n"
                                    "4. 모든 답변은 한국어로 작성하고, temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 아래 한글 키의 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"의미\": \"\", \"부정점수\": 0, \"문화적배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
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
                        # 90점 이상이면 무조건 빨간색 표시
                        if result['부정점수'] >= 90:
                            st.error(f"📍 최종 판단: {result['최종판단']}")
                        else:
                            st.warning(f"📍 최종 판단: {result['최종판단']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    st.info(f"📋 **정책 가이드라인:** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error("데이터 처리 오류")
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력해 주세요.")
