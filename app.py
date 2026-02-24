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
        word_input = st.text_input("분석할 단어:", placeholder="특수문자가 섞인 변형 단어도 분석 가능합니다 (예: n@gga, 시$발)")

        if st.button("분석"):
            with st.spinner('변형 패턴 및 글로벌 정책 맥락을 분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 다국어 비속어 변형 분석 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **특수문자 및 우회 탐지**: @, $, *, 1, 0 등 특수문자나 숫자를 섞어 금칙어를 우회하려는 패턴(예: n@gga, 시$발, n1gger)을 즉시 탐지해. "
                                    "분석 시 반드시 '원형 단어'가 무엇인지 밝히고, 검열을 피하기 위한 의도적 변형임을 명시해.\n"
                                    "2. **카테고리 분류**: 문화 이슈(인종/젠더/지역 차별) / 선정적 / 욕설 / 비속어 / 사회적 이슈 / 정치 이슈 / 일상어 중 선택.\n"
                                    "3. **변형에 대한 확신도**: 우회 수법이 명백한 경우 원형 단어와 동일하거나 더 엄격한 점수(95-100점)를 부여해.\n"
                                    "4. **항목 구성**: '표면적 의미 및 유래' 섹션에 변형 전 원형과 변형 수법을 기술하고, '판단 근거'에 우회 행위에 대한 정책적 조언을 포함해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"원형 단어 및 변형 수법 분석\", \"논란의배경\": \"원형 단어의 혐오/비하 맥락\", \"판단근거\": \"우회 시도에 대한 정책적 판단\"}}"
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
                    
                    st.write(f"🌐 **감지된 원어:** {result['언어']}")
                    
                    # 변형 수법과 원형을 보여주는 섹션
                    st.info(f"📖 **표면적 의미 및 변형 분석:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
