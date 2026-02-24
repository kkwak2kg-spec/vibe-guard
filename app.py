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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 언어학 및 젠더 이슈 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **카테고리 우선순위 조정**: '다리벌려'와 같이 성적인 행동을 강요하거나 성적 대상화가 포함된 비하 표현은 '욕설'보다 **'선정적'** 카테고리를 최우선으로 적용해.\n"
                                    "2. **어원 및 맥락의 정확성**: '느검마'를 합성어로 오해하거나 '다리벌려'를 단순 욕설로 치부하지 마. 해당 단어가 가진 성적 수치심 유발 및 젠더 갈등 유발 요소를 구체적으로 분석해.\n"
                                    "3. **점수 및 등급**: \n"
                                    "   - 직접적 선정성/성적 비하: 95-100점 (선정적)\n"
                                    "   - 직접적 패륜 욕설: 95-100점 (욕설)\n"
                                    "   - 정치/지역 비하 밈: 85-90점 (정치 이슈/커뮤니티 논란 밈)\n"
                                    "4. **항목 구성**: '표면적 의미 및 유래', '상세 맥락 및 배경', '정책 판단 근거'를 명확히 구분해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"(선정적/욕설/비속어/커뮤니티 논란 밈/정치 이슈/종교 이슈/문화 이슈/일상어 중 택1)\", \"부정점수\": 95~100, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
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
                    st.info(f"📖 **표면적 의미 및 유래:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
