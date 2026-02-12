import streamlit as st
import google.generativeai as genai
import json

st.set_page_config(page_title="Vibe Guard", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기")

api_key = st.sidebar.text_input("Gemini API Key를 입력하세요", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 모델 설정
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요")

        if st.button("분석하기"):
            # 안전 설정을 인라인으로 직접 전달 (가장 확실한 방법)
            safety = [
                {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
            
            prompt = f"""당신은 전문 게임 운영 도구입니다. 
            단어 "{word_input}"를 분석하여 반드시 아래 JSON 형식으로만 응답하세요.
            다른 말은 절대 하지 마세요.
            
            {{
              "language": "해당 언어",
              "meaning": "단어의 뜻",
              "score": 0에서 100 사이 점수,
              "reason": "부정 점수를 매긴 상세 이유"
            }}"""
            
            with st.spinner('AI 분석 중...'):
                try:
                    # 응답 생성
                    response = model.generate_content(prompt, safety_settings=safety)
                    
                    # 응답 텍스트 가져오기 (가장 안전한 방식)
                    res_text = response.candidates[0].content.parts[0].text
                    res_text = res_text.replace('```json', '').replace('```', '').strip()
                    result = json.loads(res_text)
                    
                    st.divider()
                    st.success("분석 완료!")
                    st.metric("부정 점수", f"{result['score']}점")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"🌐 **언어:** {result['language']}")
                    with col2:
                        st.write(f"📖 **뜻:** {result['meaning']}")
                    
                    st.info(f"💬 **상세 사유:** {result['reason']}")
                    
                except Exception as inner_e:
                    # 만약 진짜로 차단되었다면 상세 정보 표시
                    st.error("분석 중 오류가 발생했습니다.")
                    if "block" in str(inner_e).lower() or "safety" in str(inner_e).lower():
                        st.warning("⚠️ 이 단어는 AI 안전 정책에 의해 분석이 거부되었습니다.")
                    st.expander("개발자 에러 로그").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 API 키를 넣어주세요.")
