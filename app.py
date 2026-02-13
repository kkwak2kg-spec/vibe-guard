import streamlit as st
import google.generativeai as genai
import json

# 1. UI 설정 (가장 중립적이고 학술적인 이름으로 변경)
st.set_page_config(page_title="Linguistic DB", page_icon="🌐")
st.title("🌐 다국어 단어 정보 대시보드")

# 2. 사이드바 Key 입력
api_key = st.sidebar.text_input("Access Key (Gemini API)", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 모델 설정 (가장 안정적인 최신 표준 경로 사용)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        target = st.text_input("조회할 단어:", placeholder="예: Apple, 사과")

        if st.button("데이터 조회 시작"):
            # 안전 설정을 'BLOCK_NONE'으로 인라인 적용 (가장 확실한 방법)
            safety_config = [
                {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
            
            # AI를 절대 자극하지 않는 순수 사전적 프롬프트
            prompt = f"""
            System: Provide a dictionary-style linguistic profile.
            Word: "{target}"
            Response: Strictly JSON only.
            
            JSON Structure:
            {{
              "lang": "Detected Language",
              "definition": "Dictionary definition in Korean",
              "nuance_value": 0-100 (Usage sensitivity level),
              "context": "Common social usage in Korean"
            }}
            """
            
            with st.spinner('원격 데이터베이스 연결 중...'):
                try:
                    response = model.generate_content(prompt, safety_settings=safety_config)
                    
                    # AI가 응답을 거부했을 때(빈 응답)를 위한 안전장치
                    if not response.candidates or not response.candidates[0].content.parts:
                        st.error("해당 단어는 현재 시스템 보안 정책상 직접적인 데이터 추출이 불가능합니다.")
                        st.warning("⚠️ 고위험군 감지: 이 항목은 필터링 시스템이 답변을 거부할 만큼 민감한 표현일 가능성이 매우 높습니다.")
                    else:
                        # 정상 응답 파싱
                        res_json = response.text.replace('```json', '').replace('```', '').strip()
                        data = json.loads(res_json)
                        
                        st.divider()
                        st.success("데이터 로드 완료")
                        
                        # 시각화 (부정 점수라는 말 대신 '민감도' 사용)
                        st.metric("사회적 민감도 지수 (부정 점수)", f"{data['nuance_value']}점")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"🌐 **언어:** {data['lang']}")
                        with col2:
                            st.write(f"📖 **의미:** {data['definition']}")
                        
                        st.info(f"💬 **맥락 설명:** {data['context']}")
                        
                except Exception as inner_e:
                    st.error("데이터 처리 중 기술적인 오류가 발생했습니다.")
                    with st.expander("개발자 로그 확인"):
                        st.write(str(inner_e))
                        
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API 키를 입력하면 정보 조회가 가능합니다.")
