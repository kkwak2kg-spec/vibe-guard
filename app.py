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
        # 입력창 placeholder 빈칸 유지
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            # 로딩 문구 간소화
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 다국어 비속어 변형 분석 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **카테고리 일관성(핵심)**: 상세 설명에 '성적 비하', '성적 대상화', '신체 부위 조롱' 맥락이 포함된다면, 우회 수법이 쓰였더라도 카테고리는 반드시 '선정적'으로 분류해.\n"
                                    "2. **우회 패턴 역추적**: @, $, *, 약어(Tq 등)를 이용한 변형 패턴을 탐지하고 원형 단어를 밝혀내어 '표면적 의미 및 변형 분석' 섹션에 기술해.\n"
                                    "3. **점수 체계**: 고의적 우회 시도나 성적 비하가 포함된 단어는 예외 없이 95-100점을 부여해.\n"
                                    "4. **카테고리 목록**: 선정적 / 욕설 / 비속어 / 커뮤니티 논란 밈 / 정치 이슈 / 사회적 이슈 / 문화 이슈 / 일상어 중 선택해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"(설명과 일치하는 태그)\", \"부정점수\": 95~100, \"표면적의미\": \"원형 및 변형 수법 분석\", \"논란의배경\": \"성적/사회적 비하 맥락 상세히\", \"판단근거\": \"정책적 대응 권고\"}}"
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
                        # 설명과 일치하는 카테고리 태그 노출
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 원어:** {result['언어']}")
                    
                    # 변형 수법 및 원형 분석 복구
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
