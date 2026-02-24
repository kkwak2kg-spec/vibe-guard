import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="예: 애자, 억까, 卍")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('일관된 기준으로 한국어 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 전문가야. 일관성 있는 분석을 위해 다음 기준을 엄격히 지켜줘.\n"
                                    "1. 모든 필드의 답변 내용은 반드시 '한국어'로만 작성해.\n"
                                    "2. 점수 산정: 비하 의도가 있다면 최소 50점 이상 부여하되, 중의성이 높으면 50-70점, 명백한 혐오는 80점 이상으로 고정해.\n"
                                    "3. '애자'와 같은 단어는 한국 내에서 장애인 비하라는 강력한 역사적 맥락이 있으므로 60점 미만으로 내리지 마.\n"
                                    "4. temperature=0 설정을 통해 항상 동일한 논조와 점수를 유지해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 아래의 한글 키를 가진 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"의미\": \"\", \"부정점수\": 0, \"문화적배경\": \"\", \"최종판단\": \"\", \"운영가이드라인\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    # 결과를 파싱할 때도 한글 키를 사용합니다.
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료 (한국어 고정 모드)")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        # 한글 키 '부정점수' 사용
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **최종 판단:** {result['최종판단']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    with st.expander("🌍 문화적/역사적 배경 상세 정보"):
                        st.write(result['문화적배경'])
                        
                    st.info(f"📋 **정책 가이드라인:** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error("데이터 처리 중 오류가 발생했습니다.")
                    st.expander("에러 로그 보기").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.info("왼쪽 사이드바에 OpenAI API 키를 입력해 주세요.")
