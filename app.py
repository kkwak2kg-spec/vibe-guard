import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

# Secrets 설정 로드
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정 필요", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        
        # 입력창 placeholder는 빈칸으로 유지
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("정책 및 문화 맥락 분석"):
            with st.spinner('변칙적 우회 및 발음 유사성을 정밀 분석 중입니다...'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 및 온라인 언어 변형 분석 전문가야.\n"
                                    "1. **변칙적 우회 표현 탐지**: '곧휴(고추)', '시밤바(씨발)' 등 발음이 유사하거나 글자를 변형하여 금칙어를 우회하려는 시도를 반드시 잡아내야 해.\n"
                                    "2. **청각적 분석**: 단어를 소리 내어 읽었을 때 특정 비속어나 성적 단어와 유사하게 들린다면, 사전적 의미보다 그 '우회적 의도'를 우선적으로 판단해.\n"
                                    "3. **커뮤니티 은어 대응**: 특정 커뮤니티에서만 통용되는 비하적 밈이나 은어(흉자, 운지 등)에 대한 최신 맥락을 반영해.\n"
                                    "4. **중의성 및 정책**: 우회 표현임이 명백하면 85점 이상의 점수를 부여하고, 일상 용어와 섞일 가능성이 있다면 가이드라인에 명시해.\n"
                                    "5. 모든 답변은 한국어, temperature=0."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'의 발음 유사성과 커뮤니티 맥락을 포함하여 JSON으로 답해줘.\n"
                                           f"구조: {{\"언어\": \"\", \"유형\": \"\", \"의미\": \"사전적 의미와 우회적 의도 비교\", \"부정점수\": 0, \"문화적배경\": \"발음 유사성 및 커뮤니티 맥락\", \"최종판단\": \"차단 권고 및 오탐 가능성\", \"운영가이드라인\": \"운영팀 적용 팁\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("변칙 우회 분석 완료")
                    
                    col_score, col_decision = st.columns(2)
                    with col_score:
                        st.metric("부정/민감도 점수", f"{result['부정점수']}점")
                    with col_decision:
                        st.write(f"📍 **최종 판단:** {result['최종판단']}")
                    
                    st.write(f"🌐 **언어:** {result['언어']} / 📖 **의미:** {result['의미']}")
                    
                    with st.expander("🌍 상세 분석 및 발음 유사성 배경"):
                        st.write(result['문화적배경'])
                        
                    st.info(f"📋 **운영 가이드라인:** \n\n {result['운영가이드라인']}")
                    
                except Exception as inner_e:
                    st.error(f"오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 오류: {e}")
else:
    st.warning("API 키 설정이 필요합니다.")
