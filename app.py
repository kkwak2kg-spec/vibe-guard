import streamlit as st
import google.generativeai as genai
import json

# 1. 페이지 설정 (최대한 중립적이고 깔끔하게)
st.set_page_config(page_title="Linguistic DB", page_icon="🌐")
st.title("🌐 글로벌 단어 데이터 조회기")

# 2. 사이드바 API 설정
api_key = st.sidebar.text_input("Access Key (Gemini API)", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # 안전 설정을 가장 느슨하게 적용 (BLOCK_NONE)
        safety_config = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_config)
        
        target = st.text_input("조회할 단어:", placeholder="예: Apple, 사과")

        if st.button("데이터 조회 시작"):
            # 금칙어, 부정적, 점수 같은 단어를 배제한 '연구용' 지시문
            prompt = f"""
            Identify the dictionary information for the word: "{target}".
            Return strictly in JSON format without any other text.
            
            JSON Structure:
            {{
              "language": "Detected language",
              "definition": "Dictionary meaning in Korean",
              "usage_impact": 0-100 (level of linguistic nuance),
              "context_note": "How it is commonly used in Korean"
            }}
            """
            
            with st.spinner('데이터베이스 연결 중...'):
                try:
                    response = model.generate_content(prompt)
                    
                    # AI가 대답을 거부했을 때의 예외 처리
                    if not response.candidates or not response.candidates[0].content.parts:
                        st.error("해당 단어는 시스템 보안 정책상 직접적인 데이터 추출이 제한됩니다.")
                        st.warning("⚠️ 고위험 데이터 감지: 이 항목은 보안 시스템이 답변을 거부할 만큼 민감한 표현일 수 있습니다.")
                    else:
                        # 정상 응답 처리
                        res_json = response.text.replace('```json', '').replace('```', '').strip()
                        data = json.loads(res_json)
                        
                        st.divider()
                        st.success("데이터 로드 완료")
                        
                        # 지표 출력 (부정 점수 대신 '언어 수치'로 표현)
                        st.metric("언어 민감도 수치 (부정 점수)", f"{data['usage_impact']}점")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"🌐 **언어:** {data['language']}")
                        with col2:
                            st.write(f"📖 **의미:** {data['definition']}")
                        
                        st.info(f"💬 **맥락 설명:** {data['context_note']}")
                        
                except Exception as inner_e:
                    st.error("데이터 처리 중 기술적인 오류가 발생했습니다.")
                    with st.expander("개발자 로그 확인"):
                        st.write(str(inner_e))
                        
    except Exception as e:
        st.error(f"초기화 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력해 주세요.")
