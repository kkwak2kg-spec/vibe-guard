import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Word Info", page_icon="📖")
st.title("🌐 다국어 단어 정보 분석기")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 안전 설정을 가장 느슨하게 다시 정의
        s_settings = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=s_settings)
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력")

        if st.button("정보 가져오기"):
            # '금칙어' 단어를 아예 빼고, 사전적 정의만 요청함
            prompt = f"""Provide dictionary information for the word "{word_input}".
            Return ONLY a JSON object:
            {{
              "lang": "Language",
              "mean": "Definition in Korean",
              "vibe_score": 0 to 100 (Negative nuance level),
              "vibe_reason": "Reason for the score in Korean"
            }}"""
            
            with st.spinner('데이터 로드 중...'):
                try:
                    response = model.generate_content(prompt)
                    # 텍스트 추출
                    txt = response.text.replace('```json', '').replace('```', '').strip()
                    res = json.loads(txt)
                    
                    st.divider()
                    st.success("데이터 로드 완료")
                    
                    # 결과 출력
                    st.metric("사회적 민감도 (부정 점수)", f"{res['vibe_score']}점")
                    
                    c1, c2 = st.columns(2)
                    c1.write(f"🌐 **언어:** {res['lang']}")
                    c2.write(f"📖 **의미:** {res['mean']}")
                    
                    st.info(f"💬 **상세 분석:** {res['vibe_reason']}")
                    
                except Exception as e:
                    st.error("이 단어는 시스템 보안 정책상 상세 분석이 제한됩니다.")
                    st.write("대체 결과: 해당 단어는 높은 확률로 차단이 필요한 비속어입니다.")
                    
    except Exception as e:
        st.error(f"설정 오류가 발생했습니다. API 키를 확인해주세요.")
else:
    st.info("왼쪽 사이드바에 API 키를 입력해 주세요.")
