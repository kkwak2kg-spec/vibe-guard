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
                                    "너는 글로벌 게임 정책 결정관이자 정치/사회학 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **실명과 비하어의 점수 분리**: \n"
                                    "   - 정치적 인물 실명(예: 이승만, 윤석열, 이재명 등): 비하 의도가 없는 단순 성명은 반드시 60-70점 사이를 부여해. 역사적 논란이 있더라도 실명 자체는 제재 대상이 아님.\n"
                                    "   - 변형 비하어(예: 이죄명, 윤두창): 명백한 조롱 의도가 포함된 단어만 85-90점을 부여해.\n"
                                    "2. **할루시네이션 방지**: 실명을 '이름 변형'이라고 거짓 분석하거나 억지로 비하 수법을 지어내지 마.\n"
                                    "3. **카테고리**: 실명 및 정치적 인물은 '정치 이슈', 젠더 갈등 밈(오조오억 등)은 '문화 이슈'로 정확히 분류해.\n"
                                    "4. **설명의 객관성**: 인물 검색 시 공적 정보와 사회적 맥락만 객관적으로 서술하고, 성적 비하 등 무관한 언급을 금지해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"객관적 정의 및 성명 식별\", \"논란의배경\": \"실제 정치적/사회적 갈등 맥락\", \"판단근거\": \"운영 정책상 리스크 및 관리 가이드\"}}"
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
                        # 실명일 경우 낮은 점수가 나오도록 지침 강화
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미 및 분석:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
