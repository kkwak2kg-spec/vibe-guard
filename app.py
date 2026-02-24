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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 다음 지침을 엄격히 따라.\n\n"
                                    "1. **점수 강제 할당**: 단어에 조금이라도 비하적/정치적/갈등 유발 맥락이 존재한다면 절대 0점을 주지 마. 중의적 논란이 있는 경우 최소 50-65점 사이를 반드시 부여해.\n"
                                    "2. **텍스트 등급 출력**: '등급' 필드에는 숫자를 절대 쓰지 마. 반드시 '직접혐오', '사회적밈', '중의적논란' 중 하나를 텍스트로만 출력해.\n"
                                    "3. **표면적 의미와 논란 대조**: 'AlZubair'와 같이 인명으로 사용되는 경우, 표면적 의미(예: 아랍어권 이름)와 커뮤니티 내 비하적 활용 맥락을 대조하여 상세히 설명해.\n"
                                    "4. **항목 구성**: '운영 가이드' 섹션은 삭제하고 모든 정책적 조언은 '판단 근거'에 포함시켜.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(텍스트만)\", \"표면적의미\": \"\", \"부정점수\": 50~100, \"논란의배경\": \"\", \"판단근거\": \"전문적인 정책적 사유 및 대응 권고\"}}"
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
                        # 0점이 나오지 않도록 보정된 점수 출력
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        # 숫자가 아닌 텍스트 등급 출력
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 50:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    # 요청하신 대로 '운영 가이드'를 없애고 판단 근거만 강화
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
