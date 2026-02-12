import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Vibe Guard", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기")

# 사이드바에서 키 입력
api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요")

    if st.button("분석하기"):
        prompt = f'"{word_input}"를 분석해서 JSON으로만 답해줘. {{ "language": "언어명", "meaning": "뜻", "score": 0~100점, "reason": "이유" }}'
        with st.spinner('분석 중...'):
            try:
                response = model.generate_content(prompt)
                res_text = response.text.replace('```json', '').replace('```', '').strip()
                result = json.loads(res_text)
                
                st.metric("부정 점수", f"{result['score']}점")
                st.write(f"**언어:** {result['language']} / **뜻:** {result['meaning']}")
                st.info(f"**이유:** {result['reason']}")
            except:
                st.error("분석 실패! API 키를 확인하거나 다시 시도해주세요.")
else:
    st.warning("왼쪽 사이드바에 API 키를 넣어주세요.")