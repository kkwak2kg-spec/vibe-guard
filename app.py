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
                                    "너는 글로벌 게임 정책 결정관이야. 다음의 '카테고리별 설명 고립 지침'을 절대적으로 준수해.\n\n"
                                    "1. **욕설/비속어 설명 (고정)**: '씨발' 등 보편적 욕설은 '정치적 연결 시도'를 언급하지 마. 대신 '타인에게 불쾌감을 주는 언어적 폭력성 및 커뮤니티 정서 저해'를 중심으로 설명해.\n"
                                    "2. **일상어 설명 (고정)**: '가즈아' 등은 '긍정적 응원 및 투자 유행어'임을 명시하고 리스크를 낮게 책정해.\n"
                                    "3. **정치적 비하어 설명 (고정)**: '윤두창', '이죄명' 등은 '실명을 특정 부정적 단어와 결합한 조롱'임을 상세히 파헤쳐.\n"
                                    "4. **사회적 이슈 설명 (고정)**: '마약', '대포통장' 등은 '불법 행위의 위험성 및 사회적 부작용'을 기술해.\n"
                                    "5. **맥락 격리**: 현재 단어와 상관없는 타 카테고리의 방어 논리(예: 부당한 정치적 연결 시도 금지 등)를 다른 단어 분석에 재활용하지 마.\n"
                                    "6. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"해당 카테고리에만 부합하는 독립적 설명\", \"판단근거\": \"\"}}"
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
                    
                    # 점수에 따른 경고/안내 창 분리
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
