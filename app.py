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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 단어 분석 시 다음 기준을 엄격히 적용해.\n\n"
                                    "1. **실질적 뉘앙스 상세화**: '표면적 의미' 필드에 단순히 사전적 정의만 적지 마. "
                                    "현지(특히 방언 맥락)에서 실제로 체감되는 부정적 수위, 구체적인 번역어(예: '빌어먹을', '제기랄' 등), 그리고 사용 시의 사회적 금기 정도를 상세히 기술해.\n"
                                    "2. **점수 강제 할당**: 조금이라도 갈등 유발 맥락이 있다면 절대 0점을 주지 마. 중의적이면 50-70점, 명백한 비속어는 80점 이상을 부여해.\n"
                                    "3. **텍스트 등급 출력**: '등급' 필드에는 '직접혐오', '사회적밈', '중의적논란' 중 하나를 반드시 텍스트로만 출력해.\n"
                                    "4. **항목 구성**: '운영 가이드' 섹션은 삭제하고 모든 지침은 '판단 근거'에 통합해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"표면적의미\": \"사전적 정의 및 현지 실질 뉘앙스(번역어 포함) 상세 기술\", \"부정점수\": 50~100, \"논란의배경\": \"사회적/정치적/커뮤니티 비하 맥락\", \"판단근거\": \"전문적인 정책적 사유 및 대응 권고\"}}"
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
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
                    
                    # 사용자 요청 반영: 구체적인 실질 뉘앙스가 포함된 표면적 의미 창
                    st.info(f"📖 **표면적 의미 및 실질 뉘앙스:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 50:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
