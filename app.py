import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Vibe Guard", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기")

api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 필터를 BLOCK_NONE으로 설정해도 모델에 따라 강제 차단될 수 있음
        # 이를 위해 시스템 프롬프트를 보강합니다.
        safety_settings = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            safety_settings=safety_settings,
            system_instruction="당신은 전문 게임 운영 도구입니다. 사용자가 입력한 단어가 게임 내 금칙어로 적합한지 객관적으로 분석하세요. 어떤 비속어가 입력되어도 차단하지 말고 분석 결과만 JSON으로 응답하세요."
        )
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요")

        if st.button("분석하기"):
            # 프롬프트를 '객관적 평가' 톤으로 변경
            prompt = f"""
            Task: Evaluate the following word for game moderation.
            Word: "{word_input}"
            
            Return ONLY a JSON object:
            {{
              "language": "Detected language",
              "meaning": "Meaning in Korean",
              "score": 0 to 100 (high = toxic),
              "reason": "Reason in Korean"
            }}
            """
            
            with st.spinner('AI 분석 중...'):
                try:
                    response = model.generate_content(prompt)
                    
                    # 만약 안전 필터에 걸려 response.text가 없을 경우 처리
                    if not response.candidates or not response.candidates[0].content.parts:
                        st.error("⚠️ AI가 이 단어의 분석을 거부했습니다 (Safety Block).")
                        st.warning("이 단어는 AI조차 분석하기 거부할 정도로 수위가 높거나 위험한 단어로 판단됩니다.")
                        st.write("차단 사유:", response.candidates[0].safety_ratings)
                    else:
                        res_text = response.text.replace('```json', '').replace('```', '').strip()
                        result = json.loads(res_text)
                        
                        st.divider()
                        st.metric("부정 점수", f"{result['score']}점")
                        st.subheader(f"🔍 뜻: {result['meaning']}")
                        st.write(f"🌐 **언어:** {result['language']}")
                        st.info(f"💬 **이유:** {result['reason']}")
                        
                except Exception as inner_e:
                    st.error("분석 중 오류가 발생했습니다.")
                    with st.expander("상세 에러 보기"):
                        st.write(str(inner_e))
                        
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 넣어주세요.")
