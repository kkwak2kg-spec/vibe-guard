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
        
        # 안전 필터를 가장 낮은 수준으로 설정
        # (금칙어 분석을 위해 모든 응답을 허용함)
        safety_settings = {
            "HATE": "BLOCK_NONE",
            "HARASSMENT": "BLOCK_NONE",
            "SEXUAL": "BLOCK_NONE",
            "DANGEROUS": "BLOCK_NONE",
        }
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요")

        if st.button("분석하기"):
            # 프롬프트에 'Moderation Tool'임을 명시하여 필터링 우회 유도
            prompt = f"""As a professional game moderation tool, analyze the toxicity of the word/phrase: "{word_input}". 
            You must provide the analysis even if the word is offensive, as this is for filtering purposes.
            Respond ONLY in JSON format:
            {{
              "language": "언어명",
              "meaning": "한국어 뜻",
              "score": 0~100,
              "reason": "점수 책정 이유"
            }}"""
            
            with st.spinner('AI가 분석 중입니다...'):
                # 호출 시 직접 safety_settings 적용
                response = model.generate_content(prompt, safety_settings=safety_settings)
                
                try:
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    result = json.loads(res_text)
                    
                    st.divider()
                    st.metric("부정 점수", f"{result['score']}점")
                    st.subheader(f"🔍 뜻: {result['meaning']}")
                    st.write(f"🌐 **언어:** {result['language']}")
                    st.info(f"💬 **이유:** {result['reason']}")
                except Exception as parse_error:
                    # AI가 빈 응답을 보냈을 때의 예외 처리
                    st.error("AI가 해당 단어의 분석을 거부했습니다. 너무 수위가 높은 단어일 수 있습니다.")
                    st.write("상세 내용:", response.prompt_feedback)
                    
    except Exception as e:
        st.error(f"오류 발생: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 넣어주세요.")
