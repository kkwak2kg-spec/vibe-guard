import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어 (모든 언어 가능):", placeholder="예: 애자, 억까, 卍, KYS")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('AI 정책 전문가가 금칙어 적합성을 검토 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 정책 결정 전문가야. "
                                    "단순한 의미 분석을 넘어, 이 단어를 게임 내 '시스템 금칙어'로 등록할지 여부를 판단해줘. "
                                    "판단 시 고려할 점: "
                                    "1. 단어의 고유한 공격성 (비하, 혐오 표현 등) "
                                    "2. 오탐 가능성 (사람 이름, 일상 용어, 중립적 의미로 사용될 확률) "
                                    "3. 문화적 민감도 "
                                    "최종 의견은 '필수 차단', '주의/모니터링', '허용' 중 하나로 분류하고 그 이유를 설명해줘. "
                                    "모든 설명은 한국어로 작성해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{"
                                           f"\"language\": \"감지된 언어 및 국가\", "
                                           f"\"meaning\": \"의미 및 어원\", "
                                           f"\"score\": 0~100, "
                                           f"\"cultural_context\": \"문화적 배경\", "
                                           f"\"policy_decision\": \"필수 차단/주의 및 모니터링/허용 중 택1\", "
                                           f"\"final_opinion\": \"금칙어 적용에 대한 AI의 최종 가이드라인(오탐 가능성 포함)\""
                                           f"}}"
                            }
                        ],
                        response_format={ "type": "json_object" }
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("정책 분석 완료!")
                    
                    # 상단 지표: 점수와 정책 결정
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['score']}점")
                    with col_decision:
                        # 정책 결정에 따른 색상 강조
                        decision = result['policy_decision']
                        if "필수 차단" in decision:
                            st.error(f"📍 최종 판단: {decision}")
                        elif "주의" in decision:
                            st.warning(f"📍 최종 판단: {decision}")
                        else:
                            st.success(f"📍 최종 판단: {decision}")
                    
                    # 상세 정보
                    st.write(f"🌐 **언어 및 국가:** {result['language']}")
                    st.write(f"📖 **의미 및 어원:** {result['meaning']}")
                    
                    with st.expander("🌍 문화적/역사적 배경 보기"):
                        st.write(result['cultural_context'])
                    
                    # AI의 최종 의견 (가장 중요한 부분)
                    st.info(f"📋 **금칙어 적용 가이드라인:** \n\n {result['final_opinion']}")
                    
                except Exception as inner_e:
                    st.error("분석 중 오류가 발생했습니다.")
                    st.expander("에러 로그 보기").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 OpenAI API 키를 입력해 주세요.")
