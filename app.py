import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 로드
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정이 필요합니다", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 정책 결정관이야. 다음의 엄격한 기준을 적용해.\n\n"
                                    "1. **욕설 판정 강화**: '개년', '씨발', '븅신' 등은 일상적 중의성이 거의 없으며, 게임 내에서는 명백한 공격적 욕설로 사용되므로 90-100점을 부여해.\n"
                                    "2. **정치/사회적 비하 (80-89점)**: '윤두창', '이죄명' 등 특정 인물 타겟팅 용어. 실제 인명 가능성을 전문적 용어로 기술해.\n"
                                    "3. **항목 축소**: '운영 가이드' 섹션은 삭제하고, '판단 근거'에 모든 핵심 정책 논리를 집중시켜.\n"
                                    "4. **전문적 판단 근거**: '오탐 주의'와 같은 뻔한 말 대신, 해당 단어가 게임 커뮤니티 정서와 유저 이탈에 미치는 영향을 중심으로 구체적으로 기술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"등급\": \"(직접혐오/사회적밈/중의적논란 중 택1)\", \"의미\": \"\", \"부정점수\": 0, \"상세맥락\": \"\", \"판단근거\": \"공신력 있는 정책적 사유\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        # 90점 이상은 위험 표시
                        risk_label = " (고위험)" if result['부정점수'] >= 90 else ""
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점{risk_label}")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    if result['상세맥락']:
                        st.warning(f"⚠️ **상세 맥락:** \n\n {result['상세맥락']}")
                    
                    # 운영 가이드를 삭제하고 판단 근거를 강화하여 노출
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
