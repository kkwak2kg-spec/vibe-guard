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
            with st.spinner('글로벌 언어 및 정책 맥락을 정밀 분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 다국어 언어학 전문가야. "
                                    "이전 분석의 한국어 맥락에 매몰되지 말고, 다음 지침에 따라 독립적인 보고서를 작성해.\n\n"
                                    
                                    "1. **언어 감지 정밀화 (필수)**: 입력된 단어의 실제 언어를 정확히 판별해. 'Wichserkönig' 같은 단어는 반드시 '독일어'로 표기하고, 한국어 맥락과 섞지 마.\n\n"
                                    
                                    "2. **죄명 및 법률 용어 프로토콜 (통매음 등)**:\n"
                                    "   - 성격: 실제 법률 명칭. 그 자체로 비속어가 아님.\n"
                                    "   - 점수: **20-40점**. 카테고리: **'사회적 이슈'**.\n"
                                    "   - 설명: '통신매체이용음란죄'의 법적 정의와 해당 용어가 커뮤니티에서 법적 대응 목적으로 쓰이는 맥락을 구체적으로 기술해.\n\n"
                                    
                                    "3. **글로벌 비속어 정밀 분석 (Wichserkönig 등)**:\n"
                                    "   - 성격: 직접적인 성적 비하 및 모욕.\n"
                                    "   - 점수: **90-100점**. 카테고리: **'선정적'** 또는 **'욕설/비속어'**.\n"
                                    "   - 설명: 해당 언어권(예: 독일어)에서 이 단어가 갖는 구체적인 어원(Wichser: 수음자 + König: 왕)과 사용 시의 사회적 파장을 매우 구체적으로 서술해.\n\n"
                                    
                                    "4. **위장/잔혹 비하 (피떡갈비 등)**:\n"
                                    "   - 성격: 역사적 희생자 조롱.\n"
                                    "   - 점수: **80-88점**. 카테고리: **'문화 이슈'**.\n\n"
                                    
                                    "5. 모든 답변은 한국어로 작성하되, '언어' 필드만큼은 객관적인 원어 명칭을 기재할 것."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"사전적 의미 및 원어 해석\", \"논란의배경\": \"어원, 법적 성격, 사회적 파장 등 구체적 맥락\", \"판단근거\": \"관리 정책 제언\"}}"
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
