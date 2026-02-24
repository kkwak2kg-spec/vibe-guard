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
            # 로딩 문구를 '분석 중입니다.'로 간결하게 고정
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **사회적 이슈(범죄) 리스크 반영**: '마약', '대포통장' 등 불법 범죄와 직결된 단어는 0점이 아닌 **75-80점**의 주의 점수를 부여해. 단어 자체가 욕설은 아니더라도 범죄 조장 및 사회적 부작용 리스크를 핵심으로 분석해.\n"
                                    "2. **카테고리 정밀화**: 불법 행위는 '사회적 이슈', 젠더 갈등 밈은 '문화 이슈', 정치적 비하 밈은 '커뮤니티 논란 밈'으로 분류해.\n"
                                    "3. **위장 비하어**: '피떡갈비' 등 음식명으로 위장한 역사적 비하어는 85점을 유지하고 잔혹한 어원을 상세히 기술해.\n"
                                    "4. **실명 보호**: 정치인/역사적 인물 실명은 비하 의도가 없을 시 60-70점을 부여하고 객관적 정보만 제공해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
