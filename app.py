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
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'):
            try:
                # [개선 로직] AI에게 단순 요약이 아닌 '커뮤니티 심층 분석'을 명령
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 게임 정책 결정관이자 한국 온라인 커뮤니티 전문가야. "
                                "단순한 사전적 정의를 넘어, 아래 지침에 따라 심층 리포트를 작성해.\n\n"
                                
                                "1. **점수 및 카테고리 가이드라인 (절대 준수)**:\n"
                                "   - [욕설/선정적]: 90~100점.\n"
                                "   - [비하 밈/문화 이슈]: 80~89점. '오조오억', '피떡갈비' 등 포함.\n"
                                "   - [사회적 이슈]: 75~80점. '마약', '통매음' 등 법률/범죄 관련.\n"
                                "   - [정치 이슈/실명]: 60~70점.\n"
                                "   - [일상어]: 0~20점.\n\n"
                                
                                "2. **심층 분석 보고서 작성법**:\n"
                                "   - **표면적 의미**: 단어가 원래 가지고 있는 사전적/일상적 의미 기술.\n"
                                "   - **상세 맥락 및 배경**: 어느 커뮤니티에서 주로 쓰이는지, 어떤 특정 의도(혐오/조롱/비하 등)가 숨어 있는지, 왜 이 단어가 일반 유저들에게 불쾌감을 주는지 아주 구체적으로 서술해.\n"
                                "   - **판단 근거**: 운영 정책상 오탐 가능성과 실질적 유해성 사이에서 어떻게 판단해야 하는지 가이드를 제시해.\n\n"
                                
                                "3. **맥락 격리**: 이전 단어의 분석 내용(예: 역사적 잔혹성)을 다른 단어 분석에 절대 섞지 마."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                st.divider()
                st.success("분석 완료")
                
                # 리포트 레이아웃 구성
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{result['부정점수']}점")
                with c2: st.subheader(f"🏷️ {result['카테고리']}")
                
                st.write(f"🌐 **감지된 언어:** {result['언어']}")
                st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                
                # 배경 설명은 더 강조된 UI로 출력
                bg_text = result['논란의배경']
                if result['부정점수'] >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경 (커뮤니티 심층 분석):** \n\n {bg_text}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_text}")
                
                st.info(f"⚖️ **정책 판단 근거 및 운영 가이드:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생: {str(e)}")
else:
    st.info("API 키를 입력해주세요.")
