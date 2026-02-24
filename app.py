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
        
        # 입력창 (placeholder 제거하여 빈칸으로 유지)
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            with st.spinner('글로벌 정책 및 사회적 맥락을 정밀 분석 중입니다...'):
                try:
                    # 시스템 프롬프트: 정치인 비하, 중의성, 발음 우회 등을 모두 포함
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 전문가이자 한국 온라인 혐오 표현 및 정치적 밈 분석 전문가야. "
                                    "일관된 분석을 위해 다음 3단계 점수 및 분석 기준을 엄격히 적용해.\n\n"
                                    "1. **직접적 욕설/혐오 (90-100점)**: 명백한 욕설, 인종차별, 성희롱, 고인 모독.\n"
                                    "2. **사회적 밈/커뮤니티 비하 (80-90점)**: 정치인 비하(예: 특정 정치인 성함과 비속어의 합성어), 젠더 갈등 용어, 지역 비하. "
                                    "특히 정치인 비하의 경우 대상 인물의 직책과 비하 방식을 구체적으로 명시해.\n"
                                    "3. **발음 우회/중의적 표현 (50-70점)**: 발음 유사성 우회(예: 곧휴)나 일상 용어로 오해받을 수 있는 단어(예: 오조오억).\n\n"
                                    "주의: '윤두창'과 같은 단어는 '현직 대통령의 성과 특정 비속어를 합성하여 모욕하려는 목적으로 사용되는 정치적 비하 용어'임을 명확히 기술해. "
                                    "모든 답변은 한국어로 작성하고 temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"등급\": \"(직접혐오/사회적밈/중의적우회/커뮤니티논란어 중 택1)\", \"의미\": \"어원 및 대상(정치인 등) 구체적 명시\", \"부정점수\": 0, \"논란의배경\": \"사회적/정치적 갈등 맥락 상세히\", \"최종판단\": \"차단 권고 여부 및 오탐 주의사항\", \"운영가이드라인\": \"운영팀을 위한 실무 대응 팁\"}}"
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
                        st.metric("분쟁 리스크 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **분석 등급:** {result['등급']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    # 논란 배경 (정치적/사회적 맥락 강조)
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
