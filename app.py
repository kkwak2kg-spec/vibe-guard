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
            with st.spinner('일관된 기준으로 분석 중입니다...'):
                try:
                    # 1. temperature를 0으로 설정하여 결정론적 답변 유도
                    # 2. 점수 산정 가이드를 구체화하여 수치 통일성 확보
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 전문가야. 일관성 있는 분석을 위해 다음 기준을 엄격히 지켜줘.\n"
                                    "1. 점수 산정: 비하 의도가 1%라도 있다면 최소 50점 이상 부여하되, 중의성이 높으면 50-70점, 명백한 혐오는 80점 이상으로 고정해.\n"
                                    "2. '애자'와 같은 단어는 한국 내에서 장애인 비하라는 강력한 역사적 맥락이 있으므로, 이름으로 쓰일 가능성이 있더라도 60점 미만으로 내리지 마.\n"
                                    "3. 모든 분석은 객관적 사실과 어원에 근거하여 동일한 답변을 내놓도록 해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. 구조: {{\"language\": \"\", \"meaning\": \"\", \"score\": 0~100, \"cultural_context\": \"\", \"policy_decision\": \"\", \"final_opinion\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 # 창의성을 배제하고 일관성을 극대화
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료 (일관성 모드 적용)")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['score']}점")
                    with col_decision:
                        st.write(f"📍 **최종 판단:** {result['policy_decision']}")
                    
                    st.write(f"🌐 **언어:** {result['language']} / 📖 **의미:** {result['meaning']}")
                    st.info(f"📋 **가이드라인:** {result['final_opinion']}")
                    
                except Exception as inner_e:
                    st.error("오류 발생")
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("API 키를 입력해 주세요.")
