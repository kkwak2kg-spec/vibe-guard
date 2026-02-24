import streamlit as st
from openai import OpenAI
import json

# 1. 페이지 설정 및 스타일 정의
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
        # Placeholder 빈칸 유지 및 깔끔한 UI
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            with st.spinner('분석 중입니다.'): # 문구 고정
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 언론 심리학 전문가야. "
                                    "이전 분석의 맥락이 현재 분석에 영향을 미치는 '맥락 오염'을 엄격히 차단하라.\n\n"
                                    
                                    "### [카테고리별 독립 판정 및 점수 가이드]\n"
                                    "1. **위장 잔혹 비하 (예: 피떡갈비, 통구이)**:\n"
                                    "   - 본질: 특정 역사적 사건 희생자들을 음식에 빗대어 조롱하는 고인 모독.\n"
                                    "   - 점수: 반드시 **80-88점**. 카테고리: **'문화 이슈'**.\n\n"
                                    
                                    "2. **선정적/욕설 (예: 보빨, 씨발)**:\n"
                                    "   - 본질: 저속한 신체 비하 및 성적 수치심 유발. **절대 '역사적 사건' 언급 금지.**\n"
                                    "   - 점수: 반드시 **90-100점**. 카테고리: **'선정적'** 또는 **'욕설/비속어'**.\n\n"
                                    
                                    "3. **사회적 리스크 (예: 마약, 투약 권유)**:\n"
                                    "   - 본질: 불법 행위 조장 및 사회적 유해성. 단순 언급(75-80점)과 권유(85점+) 구분.\n"
                                    "   - 점수: **75-90점**. 카테고리: **'사회적 이슈'**.\n\n"
                                    
                                    "4. **공인/정치 및 일상어 (예: 김영삼, 가즈아)**:\n"
                                    "   - 본질: 실명 언급 자체는 중립적이나 비하 변형어는 리스크 부여.\n"
                                    "   - 점수: 실명 **60-70점**, 순수 일상어 **10-20점**. 카테고리: **'정치 이슈'** 또는 **'일상어'**.\n\n"
                                    
                                    "### [출력 정규화 규칙]\n"
                                    "- **언어**: 분석 단어명을 복사하지 말고 '한국어' 등 공식 명칭만 기재.\n"
                                    "- **카테고리**: '10-20점' 같은 점수 범위나 'Protocol' 명칭 노출 절대 금지."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"한국어\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    # 점수 및 카테고리 시각화 보정
                    col_score, col_cat = st.columns(2)
                    with col_score:
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        if result['카테고리']:
                            st.subheader(f"🏷️ {result['카테고리']}")
                        else:
                            st.subheader("🏷️ 미분류") # 카테고리 누락 방지
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    # 위험도에 따른 배경 색상 차별화
                    if result['부정점수'] >= 80:
                        st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    elif result['부정점수'] >= 60:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    else:
                        st.info(f"💡 **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
