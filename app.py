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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 '절대적 카테고리 우선순위'를 준수해.\n\n"
                                    "1. **선정적 카테고리 강제 (중요)**: 성매매, 성적 행위, 신체 부위 비하 등 성적인 맥락이 조금이라도 포함된 단어는 무조건 **'선정적'**으로 분류해. '사회적 이슈'로 분류하는 오탐을 절대 범하지 마.\n"
                                    "2. **사회적 이슈의 정의**: 마약, 대포통장, 보이스피싱 등 범죄 행위 명사 위주로만 '사회적 이슈'를 적용해. 성 관련 저속 표현은 예외 없이 '선정적'이야.\n"
                                    "3. **범죄 실행 권유**: '마약먹자' 등 실행 독려는 85점 이상을 부여해.\n"
                                    "4. **위장 비하어/인명 보호**: '피떡갈비' 등 잔혹 비하어는 85점, 정치인 실명은 60-70점대를 유지해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"(선정적/욕설/비속어/정치 이슈/사회적 이슈/문화 이슈/일상어 중 택1)\", \"부정점수\": 90, \"표면적의미\": \"\", \"논란의배경\": \"성적 수치심 및 사회적 갈등 맥락 상세히\", \"판단근거\": \"카테고리 선정 사유 및 운영 가이드\"}}"
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
