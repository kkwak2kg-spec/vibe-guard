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
                                    "너는 글로벌 게임 서비스의 정책 결정관이야. 단어 분석 시 다음의 '카테고리 엄격 구분' 원칙을 적용해.\n\n"
                                    "1. **보편적 비속어 (General Profanity)**: '븅신', '시발' 등 특정 정치/사회적 맥락 없이 오랫동안 쓰인 비속어는 '직접혐오' 혹은 '단순비속어'로 분류해. 이 경우 절대 '정치적 비하'라는 설명을 덧붙이지 마.\n"
                                    "2. **정치적/사회적 비하 밈 (Social/Political Meme)**: '윤두창', '이죄명' 등 특정 인물이나 정치적 성향을 공격하기 위해 만들어진 합성어나 신조어만 이 카테고리에 할당해. 점수는 80-90점 사이로 부여해.\n"
                                    "3. **점수 변별력**: 보편적 비속어(70-80점)와 특정 타겟 비하 밈(85-95점)의 점수 차이를 명확히 해.\n"
                                    "4. **전문적 용어**: '0.1%' 같은 표현 대신 '실제 인명 사용 가능성' 등 전문 용어를 사용하고, '실무 대응 팁' 대신 '운영 가이드'를 사용해.\n"
                                    "5. 모든 답변은 한국어, temperature=0으로 고정해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"등급\": \"\", \"의미\": \"단어의 기원과 성격\", \"부정점수\": 0, \"논란의배경\": \"사회적/정치적/일반적 맥락 구분\", \"최종판단\": \"전문적 판단 근거\", \"운영가이드\": \"단계별 대응 지침\"}}"
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
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    # 논란 배경 섹션
                    if result['부정점수'] >= 50:
                        st.warning(f"⚠️ **커뮤니티 논란 배경:** \n\n {result['논란의배경']}")
                    
                    with st.expander("🌍 운영 정책 가이드라인"):
                        st.write(f"**[판단 근거]**\n{result['최종판단']}")
                        st.write(f"---")
                        st.write(f"**[운영 가이드]**\n{result['운영가이드']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("API 키를 설정해 주세요.")
