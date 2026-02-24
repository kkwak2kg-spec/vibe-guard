import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Vibe Guard Pro", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기")

api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요 (예: 바보, 사과)")

        if st.button("분석하기"):
            with st.spinner('AI가 정밀 분석 중입니다...'):
                try:
                    # '반드시 한국어로 답변하라'는 지침을 추가했습니다.
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "너는 다국어 비속어 분석 전문가야. 모든 분석 결과(의미, 이유)는 반드시 친절한 한국어로 작성해야 해."},
                            {"role": "user", "content": f"단어 '{word_input}'를 분석해줘. 결과는 반드시 한국어로 작성하고 JSON 구조를 지켜줘: {{\"language\": \"언어\", \"meaning\": \"한국어 뜻\", \"score\": 0~100, \"reason\": \"한국어로 된 상세 이유\"}}"}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료!")
                    
                    st.metric("부정 점수", f"{result['score']}점")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"🌐 **언어:** {result['language']}")
                    with col2:
                        st.write(f"📖 **의미:** {result['meaning']}")
                    
                    # 깔끔하게 한글로 출력됩니다.
                    st.info(f"💬 **분석 사유:** {result['reason']}")
                    
                except Exception as inner_e:
                    st.error("분석 중 오류가 발생했습니다.")
                    st.expander("상세 에러 로그").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 OpenAI API 키를 입력해 주세요.")
