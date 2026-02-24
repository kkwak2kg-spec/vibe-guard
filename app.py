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
                                    "너는 글로벌 게임 서비스의 다국어 정책 결정관이야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **글로벌 언어 감지 강화**: 입력된 단어가 한국어가 아닐 가능성을 항상 염두에 둬. 특히 동남아시아(인도네시아, 베트남 등), 아랍권, 유럽권 욕설 여부를 먼저 확인해.\n"
                                    "2. **어원 분석의 정교화**: 'Bapakkau'와 같이 특정 외국어 단어(Bapak=아버지)가 포함된 경우 해당 국가의 언어와 실제 의미를 명확히 기술해. 이를 한국어 비속어로 퉁치지 마.\n"
                                    "3. **카테고리 분류**: 선정적 / 욕설 / 비속어 / 커뮤니티 논란 밈 / 정치 이슈 / 사회적 이슈 / 일상어 중 선택.\n"
                                    "4. **점수 및 판단**: 패륜적 욕설이나 심각한 혐오는 언어에 관계없이 95-100점을 부여해.\n"
                                    "5. 모든 답변은 한국어로 설명하되, '언어' 필드는 실제 해당 단어의 언어를 정확히 기입해. temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"실제 언어명\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"사전적 정의 및 언어적 기원\", \"논란의배경\": \"해당 문화권 및 커뮤니티 내 비하 맥락\", \"판단근거\": \"운영 정책상 리스크 분석\"}}"
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
