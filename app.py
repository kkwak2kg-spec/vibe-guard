import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key 설정", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'): # 문구 고정
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 한국 현대사/커뮤니티 전문가야. "
                                "단어의 표면적 글자에 꽂혀 의미를 날조하는 '환각'을 절대 금지해.\n\n"
                                "1. **'운지' 특수 분석 지침**:\n"
                                "   - 이 단어는 '운전'이나 '사고'와 무관함.\n"
                                "   - 대한민국 제16대 대통령의 서거를 비하하는 고인 모독성 비하 밈임을 명확히 기재해.\n"
                                "   - 점수는 반드시 **88~90점** 사이로 고정하고 '문화 이슈'로 분류해.\n\n"
                                "2. **설명 강화 규칙**:\n"
                                "   - [표면적 의미]: 부정형 없이 실제 변질된 용법만 기재.\n"
                                "   - [상세 맥락]: 유래된 커뮤니티와 사회적 갈등 요소를 풍부하게 서술.\n\n"
                                "3. **로직 보호**: 0점 방지 및 카테고리별 점수 하한선 준수."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0
                )
                
                result = json.loads(response.choices[0].message.content)
                score = result.get('부정점수', 0)
                category = result.get('카테고리', '미분류')
                
                # 보정: '운지' 등의 혐오 밈 0점 방지
                if category in ['문화 이슈', '문화 이슈/비하 밈'] and score < 80: score = 88

                st.divider()
                st.success("분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
