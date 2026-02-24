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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 정교한 분석 지침을 준수해.\n\n"
                                    "1. **단어 형태별 개별 분석**: 입력된 단어가 단순 명사(예: 마약)인지, 행위를 촉구하는 동사구(예: 마약먹자)인지 엄격히 구분해. 이전 분석 결과와 유사하다고 해서 설명을 돌려막지 마.\n"
                                    "2. **명사(Noun) 분석**: '마약', '대포통장' 등은 사회적 이슈(75점)로 분류하고, 불법 약물 자체의 중독성과 유해성, 사회적 부작용을 중심으로 객관적 정의를 내려.\n"
                                    "3. **동사구(Verb Phrase) 분석**: '마약먹자' 등 실행 권유형은 85-90점을 부여하고, 실제 범죄 가담 독려 및 모방 범죄 리스크를 핵심으로 분석해.\n"
                                    "4. **차별화된 리포트**: '마약' 조회 시 '행위 독려'라는 표현을 쓰지 마. 단순 명사는 '존재와 유통의 위험성'을, 동사구는 '실행 유도의 위험성'을 각각 다르게 기술해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"단어 형태에 맞는 정확한 정의\", \"논란의배경\": \"명사/동사구 구분에 따른 리스크 분석\", \"판단근거\": \"구체적인 정책 대응 가이드\"}}"
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
