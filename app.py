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
                                    "너는 글로벌 게임 정책 결정관이자 한국 온라인 커뮤니티 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **합리적 점수 체계 (중요)**: \n"
                                    "   - 직접적 패륜 욕설, 글로벌 인종차별어: 90-100점\n"
                                    "   - 음식명/일상어로 위장한 잔혹 비하어(예: 피떡갈비, 통구이 등): 80-85점. 100점 남발을 지양하되 리스크는 명확히 고지해.\n"
                                    "   - 정치적 비하 밈: 80-85점 / 정치인 실명: 60-70점\n"
                                    "2. **위장어 정밀 분석**: 표면적으로는 무해한 단어(음식 등)일 경우, '표면적 의미'에 사전적 정의를 쓰고, '논란의 배경'에 숨겨진 잔혹한 비하 맥락과 역사적 아픔을 매우 상세히 기술해.\n"
                                    "3. **카테고리 판정**: \n"
                                    "   - 집단/지역/역사 비하는 '문화 이슈' 또는 '커뮤니티 논란 밈'.\n"
                                    "   - 단순 욕설은 '욕설', 성적 비하는 '선정적'.\n"
                                    "4. **할루시네이션 방지**: 근거 없는 정치인 이름 변형 해석을 금지하고 실제 커뮤니티 사용 사례에 기반해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"사전적/외형적 의미\", \"논란의배경\": \"숨겨진 비하 맥락 및 잔혹성 상세 분석\", \"판단근거\": \"운영 정책상 리스크 및 관리 가이드\"}}"
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
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
