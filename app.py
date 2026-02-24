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
                                    "1. **변형 의도 구체화**: '이죄명', '윤두창' 등 정치인 성명을 변형한 단어 분석 시, 반드시 '원래 누구의 이름인가'와 '어떤 부정적 단어를 결합했는가'를 명확히 밝혀.\n"
                                    "2. **비하 수법 상세화**: 단순히 '비하 의도 삽입'이라 하지 마. 예: '정치인 이재명의 성명 중 [재]를 [죄(Sin/Crime)]로 교체하여 범죄자 이미지를 덧씌우려는 고의적 조롱 수법'과 같이 기술해.\n"
                                    "3. **카테고리 및 점수**: 단순 인명은 '정치 이슈'(60-70점), 비하 밈은 '커뮤니티 논란 밈' 혹은 '정치 이슈'(85점 이상)로 분류해.\n"
                                    "4. **불필요 맥락 제거**: 성적 의미가 없으면 '성적 비하와 무관'하다는 식의 언급을 일체 금지해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 85~90, \"표면적의미\": \"원본 성명 식별 및 구체적 변형 수법 분석\", \"논란의배경\": \"해당 인물을 둘러싼 정치적 갈등 및 조롱의 사회적 맥락\", \"판단근거\": \"운영 정책상 리스크 및 관리 권고\"}}"
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
