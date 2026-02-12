import streamlit as st
import google.generativeai as genai
import json

# 1. UI 설정 (최대한 깔끔하고 중립적으로)
st.set_page_config(page_title="Word Info", page_icon="🔍")
st.title("🔍 다국어 단어 정보 대시보드")

# 2. 사이드바 Key 입력
api_key = st.sidebar.text_input("Access Key", type="password")

if api_key:
    try:
        # API 초기 설정
        genai.configure(api_key=api_key)
        
        # 보안 필터를 최대한 완화 (BLOCK_NONE)
        safety_settings = [
            {"category": "HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        # 모델 로드 (가장 안정적인 경로 사용)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        word = st.text_input("조회할 단어:", placeholder="여기에 입력하세요 (예: Apple)")

        if st.button("데이터 조회"):
            # AI를 자극하지 않는 '학술적' 프롬프트
            prompt = f"""
            Provide a linguistic analysis for the word: "{word}".
            Respond ONLY in JSON format:
            {{
              "language": "Detected language",
              "definition": "Dictionary meaning in Korean",
              "nuance_score": 0-100 (level of social sensitivity),
              "context": "Usage context in Korean"
            }}
            """
            
            with st.spinner('데이터를 가져오는 중...'):
                try:
                    # 호출 시점에 안전 설정 적용
                    response = model.generate_content(prompt, safety_settings=safety_settings)
                    
                    # 결과 파싱
                    res_text = response.text.replace('```json', '').replace('```', '').strip()
                    data = json.loads(res_text)
                    
                    st.divider()
                    st.success("데이터 로드 완료")
                    
                    # 점수 시각화
                    st.metric("사회적 민감도 (부정 점수)", f"{data['nuance_score']}점")
                    
                    col1, col2 = st.columns(2)
                    col1.write(f"🌐 **언어:** {data['language']}")
                    col2.write(f"📖 **뜻:** {data['definition']}")
                    
                    st.info(f"💬 **맥락 설명:** {data['context']}")
                    
                except Exception as inner_e:
                    # 필터링에 걸렸을 때만 나오는 메시지
                    st.error("해당 단어는 시스템 보안 정책상 직접 노출이 제한됩니다.")
                    st.warning("⚠️ 고위험 단어 감지: AI 보안 시스템이 답변을 거부할 만큼 수위가 높은 표현일 가능성이 큽니다.")
                    
    except Exception as e:
        st.error(f"연결 설정 오류: {e}")
else:
    st.info("왼쪽 사이드바에 API Key를 넣어주세요.")
