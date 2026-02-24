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
                                    "너는 글로벌 게임 서비스의 정책 결정관이자 비속어 어원 전문가야. 다음 지침을 엄격히 적용해.\n\n"
                                    "1. **단어 미화 금지**: 비속어나 성적 단어를 '자산+디지털'과 같이 무해한 표준어 합성어로 억지 해석(할루시네이션)하지 마. "
                                    "실제 온라인상에서 사용되는 저급한 비속어 및 성적 맥락을 최우선으로 분석해.\n"
                                    "2. **선정적 비속어 판단**: 신체 부위나 성적 행위를 암시하는 저급한 단어(예: 자지털, 다리벌려 등)는 반드시 '선정적' 카테고리로 분류하고 95점 이상을 부여해.\n"
                                    "3. **사회적 이슈와 구분**: '대포통장'처럼 실제 법적 논란이 있는 용어만 '사회적 이슈'로 분류하고, 단순 비속어는 '선정적'이나 '비속어'로 분류해.\n"
                                    "4. **등급 출력**: '선정적', '욕설', '비속어', '사회적 이슈', '정치 이슈', '일상어' 등 텍스트로만 출력해.\n"
                                    "5. 모든 답변은 한국어, temperature=0 고정."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}'를 분석해서 JSON으로 답해줘. "
                                           f"구조: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 95~100, \"표면적의미\": \"실제 저급한 어원 및 비하 대상 상세 기술\", \"논란의배경\": \"성적 수치심 유발 및 커뮤니티 정서 저해 맥락\", \"판단근거\": \"운영 정책상 차단 필요성 및 리스크 분석\"}}"
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
