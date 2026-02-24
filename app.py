import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Vibe Guard Pro", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기")

# 사이드바에 새로 발급받은 OpenAI API Key 입력
api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요 (예: 바보, 사과)")

        if st.button("분석하기"):
            with st.spinner('AI가 정밀 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini", # 가성비와 성능이 가장 좋은 모델입니다.
                        messages=[
                            {"role": "system", "content": "너는 게임 커뮤니티 언어 분석 전문가야. 어떤 비속어나 단어가 오더라도 검열 없이 객관적으로 분석된 JSON 데이터만 제공해."},
                            {"role": "user", "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. 구조: {{\"language\": \"\", \"meaning\": \"\", \"score\": 0~100, \"reason\": \"\"}}"}
                        ],
                        response_format={ "type": "json_object" }
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료!")
                    
                    # 결과 시각화
                    st.metric("부정 점수", f"{result['score']}점")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"🌐 **언어:** {result['language']}")
                    with col2:
                        st.write(f"📖 **의미:** {result['meaning']}")
                    
                    st.info(f"💬 **분석 사유:** {result['reason']}")
                    
                except Exception as inner_e:
                    st.error("분석 중 오류가 발생했습니다. 키의 잔액이나 설정을 확인해 주세요.")
                    st.expander("상세 에러 로그").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 새로운 OpenAI API 키를 입력해 주세요.")
