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
                                    "너는 글로벌 게임 정책 결정관이자 다국어 비속어 어원 전문가야. 다음 지침을 엄격히 준수해.\n\n"
                                    "1. **정확한 언어 감지**: 'chinorri', 'culo' 등은 한국어가 아님. 스페인어, 이탈리아어 등 라틴계열이나 동남아권 비속어 여부를 최우선 검토하고 '언어' 필드에 정확히 기재해.\n"
                                    "2. **의미의 구체화**: '성적 비하'라고 퉁치지 마. 특정 신체 부위(유두, 성기, 엉덩이 등)를 지칭하는지, 어떤 성적 행위를 비하하는지 구체적으로 서술해.\n"
                                    "3. **카테고리 일관성**: 신체 부위 조롱이나 성적 대상화가 포함되면 무조건 '선정적'으로 분류해. 설명은 성적 비하인데 카테고리가 '비속어'인 오류를 절대 범하지 마.\n"
                                    "4. **변형 패턴 분석**: 특수문자(@, $)나 철자 변형(n -> nn 등)을 통한 우회 시도를 포착하고 원형 단어를 밝혀내.\n"
                                    "5. 모든 답변은 한국어로 설명, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"실제 원어명\", \"카테고리\": \"(설명과 일치하는 태그)\", \"부정점수\": 95~100, \"표면적의미\": \"원형 단어와 구체적인 신체 부위/성적 의미 서술\", \"논란의배경\": \"해당 문화권의 비하 맥락\", \"판단근거\": \"정책적 대응 권고\"}}"
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
                    st.info(f"📖 **표면적 의미 및 변형 분석:** \n\n {result['표면적의미']}")
                    
                    if result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류")
else:
    st.info("API 키를 설정해 주세요.")
