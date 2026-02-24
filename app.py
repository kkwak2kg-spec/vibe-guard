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
                                    "너는 글로벌 게임 정책 결정관이자 정치/사회학 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **실명과 변형어 엄격 구분**: 정치인의 정확한 성명(예: 윤석열, 이재명)은 그 자체로 비하어가 아님. 절대 '변형된 이름'이라고 거짓 분석하지 마.\n"
                                    "2. **점수 이원화**: \n"
                                    "   - 정치인 실명: 60-70점 (정치 이슈 카테고리). 분쟁 소지가 있으나 차단 권고 대상은 아님.\n"
                                    "   - 변형 비하어(예: 이죄명, 윤두창): 85-90점 (커뮤니티 논란 밈). 명백한 조롱 의도가 포함됨.\n"
                                    "3. **할루시네이션 방지**: 단어에 포함된 한자를 영어(Steel 등)로 억지 연결하여 변형 수법이라고 지어내지 마. 실제 변형된 철자가 존재할 때만 기술해.\n"
                                    "4. **설명의 객관성**: 실명 검색 시에는 인물의 현재 직위와 사회적 위치만 객관적으로 서술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"원본 명칭 여부 및 객관적 정보\", \"논란의배경\": \"실제 정치적 갈등 맥락\", \"판단근거\": \"운영 정책상 리스크 및 관리 권고\"}}"
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
