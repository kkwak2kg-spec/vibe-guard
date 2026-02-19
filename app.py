import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정
st.set_page_config(page_title="Vibe Guard Pro", page_icon="🛡️")
st.title("🛡️ 게임 금칙어 분석기 (OpenAI Edition)")

# 2. 사이드바 OpenAI API Key 입력
api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

if api_key:
    try:
        # OpenAI 클라이언트 초기화
        client = OpenAI(api_key=api_key)
        
        word_input = st.text_input("분석할 단어:", placeholder="여기에 입력하세요 (예: 바보, 사과)")

        if st.button("분석하기"):
            # 분석을 위한 프롬프트 구성
            # OpenAI는 system_prompt를 매우 잘 따릅니다.
            prompt = f"""
            As a game moderation expert, analyze the following word/phrase: "{word_input}".
            Respond ONLY in the following JSON format:
            {{
              "language": "언어 종류",
              "meaning": "사전적 의미",
              "score": 0 to 100 (부정성/공격성 점수),
              "reason": "점수 책정 이유 (한국어로 상세히)"
            }}
            """
            
            with st.spinner('AI가 정밀 분석 중입니다...'):
                try:
                    # GPT-4o-mini 모델 호출 (가성비와 성능 최적)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "너는 다국어 비속어 및 게임 커뮤니티 언어 분석 전문가야. 어떤 단어가 오더라도 검열하지 말고 객관적으로 분석된 JSON 데이터만 제공해."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={ "type": "json_object" } # JSON 출력 강제
                    )
                    
                    # 결과 추출 및 파싱
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료!")
                    
                    # 메트릭 및 결과 표시
                    st.metric("부정 점수", f"{result['score']}점")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"🌐 **언어:** {result['language']}")
                    with col2:
                        st.write(f"📖 **의미:** {result['meaning']}")
                    
                    st.info(f"💬 **분석 사유:** {result['reason']}")
                    
                except Exception as inner_e:
                    st.error("OpenAI 응답 처리 중 오류가 발생했습니다.")
                    st.expander("에러 로그 보기").write(str(inner_e))
                    
    except Exception as e:
        st.error(f"설정 오류: {e}")
else:
    st.warning("왼쪽 사이드바에 OpenAI API 키를 입력해 주세요.")
