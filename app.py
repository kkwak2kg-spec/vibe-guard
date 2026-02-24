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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 정교한 점수 산정 체계를 준수해.\n\n"
                                    "1. **범죄 키워드 등급화**: \n"
                                    "   - 단순 범죄 명사(예: 마약, 대포통장): 75점 수준의 사회적 이슈로 분류해.\n"
                                    "   - 실행 권유 및 독려형(예: 마약먹자, 통장팔아요): 단순 명사보다 높은 **85-90점**을 부여해. 이는 실제 범죄 가담 및 유해 행위 유도로 간주되어 리스크가 훨씬 큼.\n"
                                    "2. **카테고리**: 불법 행위 관련은 '사회적 이슈'로 분류하되, 실행 권유형은 판단 근거에 '행위 독려 리스크'를 명시해.\n"
                                    "3. **위장 비하어**: '피떡갈비' 등 잔혹 비하어는 85점을 유지해.\n"
                                    "4. **실명 보호**: 정치인 실명은 비하 의도가 없을 시 60-70점을 유지해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"행위의 유해성 및 독려 리스크 중심\", \"판단근거\": \"단순 언급과 실행 권유의 차이점 포함\"}}"
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
