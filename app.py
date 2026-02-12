import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Vibe Guard", page_icon="🛡️")
st.title("🛡️ 다국어 언어 분석기")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 필터를 BLOCK_NONE으로 설정하여 최대한 허용
        safety = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        # 시스템 지시문을 중립적인 언어학자로 설정
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            safety_settings=safety,
            system_instruction="당신은 사전적 의미를 분석하는 언어학 연구원입니다. 모든 답변은 JSON 형식으로만 하며, 단어의 중립적인 속성을 수치화합니다."
        )
        
        word_input = st.text_input("분석할 텍스트:", placeholder="분석하고 싶은 단어를 입력하세요")

        if st.button("데이터 분석 시작"):
            # '금칙어', '나쁜' 같은 단어를 배제한 중립적 프롬프트
            prompt = f"""Analyze the dictionary properties of the input: "{word_input}".
            Return ONLY a JSON object:
            {{
              "lang": "언어명",
              "def": "사전적 의미",
              "impact": 0~100 (사회적 민감도 수치),
              "note": "언어학적 특징 분석"
            }}"""
            
            with st.spinner('서버 분석 중...'):
                try:
                    response = model.generate_content(prompt)
                    
                    # 텍스트 추출 시도
                    if response.candidates[0].content.parts:
                        res_text = response.text.replace('```json', '').replace('```', '').strip()
                        result = json.loads(res_text)
                        
                        st.divider()
                        st.success("데이터 추출 성공")
                        st.metric("민감도 지수 (부정 점수)", f"{result['impact']}점")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"🌐 **언어:** {result['lang']}")
                        with col2:
                            st.write(f"📖 **의미:** {result['def']}")
                        
                        st.info(f"💬 **상세 분석:** {result['note']}")
                    else:
                        st.error("시스템이 해당 단어의 데이터를 반환하지 않았습니다.")
                        
                except Exception as inner_e:
                    st.error("분석 중 일시적인 오류가 발생했습니다.")
                    st.expander("오류 상세 로그").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 넣어주세요.")
