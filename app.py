import streamlit as st
import google.generativeai as genai
import json

# 1. UI 설정 (최대한 학술적이고 중립적인 디자인)
st.set_page_config(page_title="Linguistic Analyzer", page_icon="🔍")
st.title("🔍 글로벌 언어 데이터 분석기")

# 2. 사이드바 API 설정
api_key = st.sidebar.text_input("Access Key (Gemini API)", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # 모델 설정 (가장 안정적인 경로 사용)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        target = st.text_input("조회할 텍스트:", placeholder="예: Apple, 사과")

        if st.button("데이터 조회"):
            # 안전 설정을 가장 느슨하게 (하지만 문구는 자극적이지 않게)
            safety_settings = [
                {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
            ]
            
            # AI를 자극하지 않는 '학술적 연구용' 프롬프트
            prompt = f"""
            Identify the dictionary properties of the input: "{target}".
            Provide the result ONLY in the following JSON format:
            {{
              "language": "Detected language",
              "definition": "Dictionary meaning in Korean",
              "score": 0 to 100 (Usage sensitivity level),
              "context": "Contextual usage analysis in Korean"
            }}
            """
            
            with st.spinner('데이터베이스 연결 중...'):
                try:
                    # 응답 생성
                    response = model.generate_content(prompt, safety_settings=safety_settings)
                    
                    # 응답이 비어있거나 필터링된 경우 처리
                    if not response.candidates or not response.candidates[0].content.parts:
                        # 검열에 걸렸을 때만 '고위험' 메시지 출력
                        st.error("해당 텍스트는 시스템 보안 정책상 직접 노출이 제한됩니다.")
                        st.warning("⚠️ 고위험 텍스트 감지: 필터링 시스템이 답변을 거부할 만큼 민감한 표현일 수 있습니다.")
                    else:
                        # 정상 응답 파싱
                        res_text = response.text.replace('```json', '').replace('```', '').strip()
                        data = json.loads(res_text)
                        
                        st.divider()
                        st.success("데이터 로드 성공")
                        
                        # 지표 출력 (부정 점수 대신 '민감도' 사용)
                        st.metric("사회적 민감도 지수 (부정 점수)", f"{data['score']}점")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"🌐 **언어:** {data['language']}")
                        with col2:
                            st.write(f"📖 **의미:** {data['definition']}")
                        
                        st.info(f"💬 **상세 분석:** {data['context']}")
                    
                except Exception as inner_e:
                    # API 호출 자체의 에러 (404, 403 등) 처리
                    st.error("데이터를 가져오는 중 오류가 발생했습니다.")
                    with st.expander("개발자 로그 확인"):
                        st.write(str(inner_e))
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API Key를 넣어주세요.")
