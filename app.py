import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Vibe Guard", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기")

# 사이드바에서 키 입력
api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 안전 필터 해제 설정
        safety_settings = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요")

        if st.button("분석하기"):
            # 프롬프트를 조금 더 명확하게 수정
            prompt = f"""Analyze the word or phrase "{word_input}" for a game moderation system. 
            Respond ONLY in JSON format with the following structure:
            {{
              "language": "language name",
              "meaning": "meaning in Korean",
              "score": score from 0 to 100,
              "reason": "reason for the score in Korean"
            }}"""
            
            with st.spinner('AI가 분석 중입니다...'):
                response = model.generate_content(prompt)
                
                # AI 답변이 비어있는지 확인
                if not response.text:
                    st.error("AI가 답변을 거부했습니다. 다른 단어를 시도해보세요.")
                else:
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    result = json.loads(res_text)
                    
                    st.divider()
                    st.metric("부정 점수", f"{result['score']}점")
                    st.subheader(f"🔍 뜻: {result['meaning']}")
                    st.write(f"🌐 **언어:** {result['language']}")
                    st.info(f"💬 **이유:** {result['reason']}")
    except Exception as e:
        st.error(f"오류 발생: {e}") # 어떤 에러인지 정확히 출력
else:
    st.warning("왼쪽 사이드바에 API 키를 넣어주세요.")
