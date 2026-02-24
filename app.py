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
                    # [구조적 해결] 각 단어 유형별로 '절대 금지 키워드'를 설정하여 맥락 전이 방지
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 언어 심리학 전문가야. "
                                    "이전 분석 결과의 키워드를 현재 분석에 절대 섞지 마라. "
                                    "특히 선정적 단어와 역사적 비하 단어의 배경 설명을 엄격히 분리해.\n\n"
                                    
                                    "### [독립 판정 프로토콜]\n"
                                    "1. **선정적/욕설 (보빨, 씨발 등)**:\n"
                                    "   - 배경 설명에 '역사적 사건', '희생자 조롱', '지역 비하' 단어를 절대 쓰지 마.\n"
                                    "   - 오직 성적 수치심, 저속한 신체 비하, 언어적 폭력성만 기술해.\n"
                                    "   - 점수: 90-100점. 카테고리: '선정적' 또는 '욕설/비속어'.\n\n"
                                    
                                    "2. **잔혹 비하/문화 이슈 (피떡갈비 등)**:\n"
                                    "   - 희생자를 음식에 비유한 잔혹성과 고인 모독의 역사적 맥락을 상세히 기술해.\n"
                                    "   - 점수: 80-88점. 카테고리: '문화 이슈'.\n\n"
                                    
                                    "3. **사회적 이슈 (마약 등)**:\n"
                                    "   - 불법 행위의 위험성과 모방 범죄 리스크만 기술해.\n"
                                    "   - 점수: 75-80점. 카테고리: '사회적 이슈'.\n\n"
                                    
                                    "4. **공통 규칙**:\n"
                                    "   - 언어 필드에 단어명 복사 금지 (예: '마약' 분석 시 언어는 '한국어').\n"
                                    "   - 카테고리에 점수 범위(10-20점 등) 표기 금지."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"한국어\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"해당 단어 고유의 독립적 맥락만 기술\", \"판단근거\": \"\"}}"
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
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    # 80점 이상의 고위험군은 상세 배경을 더 강조하여 표시
                    if result['부정점수'] >= 80:
                        st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    else:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
