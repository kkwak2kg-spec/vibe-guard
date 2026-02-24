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

        # 버튼 명칭을 '분석'으로 간소화
        if st.button("분석"):
            # 스피너 문구를 '분석 중입니다.'로 간소화
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 전문가야. 다음 기준을 엄격히 적용해 분석해.\n\n"
                                    "1. **카테고리 및 점수 필수 원칙**: 다음 카테고리 중 하나를 선택하고, 절대 0점이나 낮은 점수로 회피하지 마.\n"
                                    "   - 선정적 / 욕설 / 비속어 / 커뮤니티 논란 밈 / 정치 이슈 / 종교 이슈 / 문화 이슈 / 일상어\n"
                                    "2. **점수 하한선**: 명백한 '욕설'이나 '선정적' 단어는 반드시 90-100점을 부여해. '느금마'가 5점이 나오는 것은 절대 금지야.\n"
                                    "3. **표면적 의미 및 유래**: 단어의 사전적 정의와 실제 사용되는 구체적인 유래(줄임말 포함)를 반드시 기술해.\n"
                                    "4. **판단 근거**: '운영 가이드' 섹션을 따로 만들지 말고, 모든 정책적 사유와 대응 지침을 '판단근거' 항목에 통합해 기술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 90~100, \"표면적의미\": \"사전적 정의 및 줄임말 유래 포함\", \"논란의배경\": \"사회적/선정적/비하 맥락 상세히\", \"판단근거\": \"전문적 정책 사유 및 대응 권고\"}}"
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
                    
                    st.write(f"🌐 **언어:** {result['언어']}")
                    
                    # '표면적 의미 및 유래' 항목 복구
                    st.info(f"📖 **표면적 의미 및 유래:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    # 정책 판단 근거 통합 노출
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
