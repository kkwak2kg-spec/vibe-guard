import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Word Analyzer", page_icon="🍎")
st.title("🍎 다국어 단어 분석기")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 모델 설정 (가장 표준적인 이름 사용)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        word_input = st.text_input("분석할 단어:", placeholder="예: 사과, 바보")

        if st.button("분석 시작"):
            # 안전 설정: 모든 검열을 해제하여 분석 도구로서 작동하게 함
            safety = [
                {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
            
            prompt = f"""Analyze the word "{word_input}". 
            Respond ONLY in JSON format like this:
            {{
              "language": "언어명",
              "meaning": "한국어 뜻",
              "score": 0~100,
              "reason": "이유"
            }}"""
            
            with st.spinner('AI 분석 중...'):
                try:
                    # 실제 API 호출
                    response = model.generate_content(prompt, safety_settings=safety)
                    
                    # 결과 파싱
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    result = json.loads(res_text)
                    
                    st.divider()
                    st.metric("부정 점수", f"{result['score']}점")
                    st.write(f"🌐 **언어:** {result['language']} / 📖 **뜻:** {result['meaning']}")
                    st.info(f"💬 **사유:** {result['reason']}")
                    
                except Exception as inner_e:
                    st.error("데이터를 가져오는 데 실패했습니다.")
                    st.expander("에러 로그 보기").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"초기 설정 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 넣어주세요.")
