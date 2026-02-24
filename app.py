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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 '카테고리 판정 우선순위'를 절대적으로 준수해.\n\n"
                                    "1. **욕설/비속어 우선**: '씨발' 등 보편적인 욕설은 사회적 갈등 맥락이 있더라도 무조건 '욕설'로 분류해. '문화 이슈'로 돌려 막지 마.\n"
                                    "2. **인명 보호**: 실존 정치인/역사적 인물 실명(이승만, 윤석열 등)은 비하 변형이 없는 한 '정치 이슈'로 분류하고 60점대를 유지해. 절대 85점 이상 주지 마.\n"
                                    "3. **밈과 이슈의 구분**: '오조오억' 등 젠더 갈등은 '문화 이슈', '이죄명' 등 조롱 밈은 '커뮤니티 논란 밈'으로 세분화해. 억지로 정치인과 엮지 마.\n"
                                    "4. **선정성**: 성적 비하/신체 조롱은 '선정적' 카테고리를 고수해.\n"
                                    "5. **할루시네이션 금지**: 모르는 단어를 정치인 이름의 변형이라고 지어내지 마. 근거가 없으면 '일상어' 혹은 '불명'으로 처리해.\n"
                                    "6. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"(욕설/선정적/비속어/정치 이슈/문화 이슈/커뮤니티 논란 밈/일상어 중 택1)\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
