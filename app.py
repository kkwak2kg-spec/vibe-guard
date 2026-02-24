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
                                    "너는 글로벌 게임 정책 결정관이자 한국 온라인 커뮤니티 전문가야. "
                                    "아래 '카테고리별 격리 판정 프로토콜'을 기계적으로 준수해.\n\n"
                                    
                                    "### [PROTOCOL 1: 욕설 및 선정성]\n"
                                    "- 대상: 씨발, 보빨, chinorri 등 직접적인 욕설이나 성적 비하.\n"
                                    "- 점수: 반드시 **90-100점** 고정.\n"
                                    "- 카테고리: '욕설/비속어' 또는 '선정적'으로 표시.\n\n"
                                    
                                    "### [PROTOCOL 2: 위장 혐오 및 문화 이슈]\n"
                                    "- 대상: 피떡갈비, 홍어, 오조오억, 윤두창 등 음식명 위장 비하어나 젠더/정치 갈등 밈.\n"
                                    "- **중요**: '피떡갈비'는 음식명이 아닌 고인 모독형 혐오 표현임. 절대 일상어로 분류하지 마.\n"
                                    "- 점수: 반드시 **80-88점** 고정.\n"
                                    "- 카테고리: '문화 이슈' 또는 '커뮤니티 논란 밈'으로 표시.\n\n"
                                    
                                    "### [PROTOCOL 3: 불법 및 사회적 리스크]\n"
                                    "- 대상: 마약, 대포통장 등 범죄 관련.\n"
                                    "- 점수: 단순 명사는 **75-80점**, 실행 권유(마약먹자)는 **85-90점**.\n"
                                    "- 카테고리: '사회적 이슈'로 표시.\n\n"
                                    
                                    "### [PROTOCOL 4: 실명 및 일상어]\n"
                                    "- 대상: 이승만, 윤석열(실명), 가즈아 등.\n"
                                    "- 점수: 실명은 **60-70점**, 순수 일상어는 **10-20점**.\n"
                                    "- 카테고리: '정치 이슈' 또는 '일상어'로 표시.\n\n"
                                    
                                    "### [언어 감지 및 출력 규칙]\n"
                                    "1. '언어' 필드에는 단어명(예: 마약)을 그대로 쓰지 말고 반드시 '한국어' 또는 해당 언어의 정식 명칭만 기재해.\n"
                                    "2. 카테고리 필드에는 '10-20점' 같은 숫자 범위를 쓰지 말고 지정된 명칭만 기재해."
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
                    
                    col_score, col_cat = st.columns(2)
                    with col_score:
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    # 언어 필드 환각 방지 레이어
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
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
