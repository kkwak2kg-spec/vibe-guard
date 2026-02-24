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
                                    "너는 글로벌 게임 정책 결정관이자 한국 커뮤니티 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **정치 이슈 오남용 금지**: '오조오억', '허버허버' 등은 정치인 이름과 무관함. 절대 '정치인 이름 변형'이라고 거짓 분석하지 마.\n"
                                    "2. **카테고리 정밀화**: \n"
                                    "   - **문화 이슈**: 젠더 갈등(예: 오조오억), 인종 차별, 지역 비하.\n"
                                    "   - **정치 이슈**: 실제 정치인 실명 및 관련 비하어.\n"
                                    "   - **선정적/욕설**: 성적 표현 및 패륜 욕설.\n"
                                    "3. **정확한 유래 기술**: '오조오억'은 아주 많음을 뜻하는 표현에서 유래했으나 최근 젠더 갈등 맥락에서 남성 혐오 표현으로 논란이 된 점을 구체적으로 설명해.\n"
                                    "4. **사실 관계 우선**: 모르는 단어는 억지로 정치인과 연결하지 말고, '데이터상 확인되지 않는 유래'임을 명시하거나 언어적 특징만 분석해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 85, \"표면적의미\": \"사전적 유래 및 실제 의미\", \"논란의배경\": \"커뮤니티 내 갈등(젠더/정치 등) 맥락 상세히\", \"판단근거\": \"운영 정책상 리스크 및 관리 권고\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col_score, col_cat = st.columns(2)
                    with col_score:
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미 및 유래 분석:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
