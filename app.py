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
        
        # 안전 필터 설정
        safety_settings = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        # 모델 이름 후보군 (버전에 따라 다를 수 있어 안전하게 설정)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요")

        if st.button("분석하기"):
            prompt = f"""As a game moderation tool, analyze the word/phrase: "{word_input}". 
            Respond ONLY in JSON format:
            {{
              "language": "언어명",
              "meaning": "한국어 뜻",
              "score": 0~100,
              "reason": "점수 책정 이유"
            }}"""
            
            with st.spinner('AI가 분석 중입니다...'):
                try:
                    # 안전 필터와 함께 호출
                    response = model.generate_content(prompt, safety_settings=safety_settings)
                    
                    # 텍스트 추출 시도
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    result = json.loads(res_text)
                    
                    st.divider()
                    st.metric("부정 점수", f"{result['score']}점")
                    st.subheader(f"🔍 뜻: {result['meaning']}")
                    st.write(f"🌐 **언어:** {result['language']}")
                    st.info(f"💬 **이유:** {result['reason']}")
                    
                except Exception as inner_e:
                    # 상세 에러 출력으로 원인 파악
                    st.error(f"분석 중 오류가 발생했습니다.")
                    st.expander("에러 로그 보기").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 넣어주세요.")
