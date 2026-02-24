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
        # 입력창 placeholder를 빈칸으로 설정
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            # 로딩 문구를 '분석 중입니다.'로 간소화
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 다국어 비속어 변형 분석 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **특수문자 및 우회 탐지**: @, $, *, 1, 0 등 특수문자나 숫자를 섞어 금칙어를 우회하려는 패턴을 즉시 탐지해.\n"
                                    "2. **원형 분석**: 변형된 단어를 감지하면 반드시 '원형 단어'가 무엇인지 밝히고, 어떤 수법으로 우회했는지 '표면적 의미 및 변형 분석' 섹션에 상세히 기술해.\n"
                                    "3. **카테고리 분류**: 문화 이슈 / 선정적 / 욕설 / 비속어 / 사회적 이슈 / 정치 이슈 / 일상어 중 가장 적합한 하나를 선택해.\n"
                                    "4. **점수 정책**: 인종 차별 및 혐오 표현의 변형은 예외 없이 95-100점을 부여하고, 고의적인 우회 시도 그 자체를 정책적 위험 요소로 판단해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"원형 단어와 변형 수법 분석\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
                    
                    # 변형 수법과 원형을 상단에 노출
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
