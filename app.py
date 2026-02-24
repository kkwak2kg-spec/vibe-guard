import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정
st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# 2. API 키 로드 (Streamlit Secrets 우선)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정이 필요합니다", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        
        # 입력창 (placeholder 없이 빈칸 유지)
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            # 요청하신 대로 스피너 문구를 간소화했습니다.
            with st.spinner('분석 중입니다.'):
                try:
                    # 시스템 프롬프트: 점수 0점 방지 및 정치적 비하 구체화 로직 강화
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 수석 정책 결정관이자 언어학 전문가야. "
                                    "너의 임무는 단어의 '분쟁 리스크'를 수치화하는 것이며, 정치적 중립성을 이유로 점수 부여를 회피해서는 안 돼.\n\n"
                                    "1. **점수 부여 필수 원칙**: 모든 분석 결과에는 반드시 0보다 큰 점수를 부여해. 특히 정치적 비하, 젠더 갈등 용어는 운영상 '고위험'군이므로 최소 80점 이상을 강제로 할당해. 절대 0점을 출력하지 마.\n"
                                    "2. **비하 대상 구체화**: '윤두창'과 같은 단어는 '현직 대통령에 대한 모욕적 비하'임을 명확히 명시해. 특정 인물을 타겟팅한 변형 욕설은 가장 높은 수준의 분쟁 리스크로 간주해.\n"
                                    "3. **3단계 기준 재확인**:\n"
                                    "   - 직접 욕설/패륜: 90-100점\n"
                                    "   - 사회적 밈/정치인 비하: 80-95점\n"
                                    "   - 중의적 우회/커뮤니티 논란어: 50-75점\n"
                                    "4. 모든 답변은 한국어, temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(직접혐오/사회적밈/중의적우회/커뮤니티논란어 중 택1)\", \"의미\": \"어원 및 비하 대상 구체적 명시\", \"부정점수\": 50~100, \"논란의배경\": \"사회적/정치적 갈등 맥락 상세히\", \"최종판단\": \"차단 권고 여부 및 오탐 주의사항\", \"운영가이드라인\": \"운영팀 실무 대응 팁\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    # 지표 레이아웃
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        # 리스크 점수가 80점 이상인 경우 강조
                        score = result['부정점수']
                        st.metric("분쟁 리스크 점수", f"{score}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    # 논란 배경 섹션
                    st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 상세 가이드"):
                        st.write(f"**판단 근거:** {result['최종판단']}")
                        st.write(f"**실무 대응 팁:** {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("API 키가 설정되지 않았습니다. Streamlit Secrets를 확인하거나 사이드바에 입력해 주세요.")
