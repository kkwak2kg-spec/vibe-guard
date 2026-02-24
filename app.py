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
                                    "너는 글로벌 게임 정책 결정관이자 다국어 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **언어 감지 정밀화 (최우선)**: 입력된 단어의 실제 언어를 정확히 판별해. 'Wichserkönig' 같은 독일어 비속어는 반드시 '독일어'로 표기하고 한국어로 오인하지 마.\n"
                                    "2. **죄명 및 법률 용어 판정 (통매음 등)**: '통매음'은 저속한 비속어가 아닌 법률상 죄명임. 리스크 점수를 20-40점으로 낮추고 '사회적 이슈'로 분류해 정확한 법적 정의를 제공해.\n"
                                    "3. **비속어/비하어 분석**: 독일어 비속어 등 글로벌 욕설은 어원(Wichser: 수음자 등)을 포함해 매우 구체적으로 분석하고 90-100점을 부여해.\n"
                                    "4. **위장 혐오 표현**: '피떡갈비' 등은 음식명이 아닌 고인 모독형 혐오임을 명시하고 80-88점을 부여해.\n"
                                    "5. **맥락 격리**: 이전 대화의 분석 논리(예: 역사적 비극 등)를 현재 분석 단어와 상관없이 섞어 쓰지 마.\n"
                                    "6. 모든 답변은 한국어로 작성하되 '언어' 필드에는 객관적인 언어 명칭만 기재해."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"원어 해석 포함\", \"논란의배경\": \"어원 및 법적/사회적 맥락 상세 기술\", \"판단근거\": \"\"}}"
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
                        st.subheader(f"🏷️ {result['카테고리'] if result['카테고리'] else '미분류'}")
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 80:
                        st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    elif result['부정점수'] >= 40:
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
