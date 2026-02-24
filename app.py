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
        with st.spinner('분석 중입니다.'): 
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이야. 단어별 유해성의 '경중'을 아래 기준에 따라 엄격히 구분해.\n\n"
                                "1. **리스크 등급별 점수 강제 배분**:\n"
                                "   - [고인 모독/반인륜적 비하]: **88~92점**. '운지'와 같이 죽음이나 비극적 사건을 조롱하는 단어.\n"
                                "   - [젠더 갈등/사회적 분쟁 밈]: **80~85점**. '오조오억'과 같이 특정 집단을 조롱하지만 패륜적 성격은 낮은 단어.\n"
                                "   - [욕설/비속어]: 원형은 95점 이상, 변형어(시밤 등)는 75~85점.\n"
                                "   - [일상어]: 0~20점.\n\n"
                                "2. **설명 작성 지침**:\n"
                                "   - '운지' 분석 시: 반드시 '고인 모독' 및 '서거 조롱'의 맥락을 구체적으로 포함해.\n"
                                "   - '오조오억' 분석 시: '젠더 갈등' 및 '상대방 조롱'의 맥락 위주로 서술하되 고인 모독과는 차별화해.\n"
                                "3. **절대 금지**: 분석 근거에 한국어 욕설 발음 유사성 언급 금지."
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
                
                # [보정 로직] 단어 성격에 따른 점수 분별력 강화
                if "운지" in word_input and score < 88: score = 90
                elif "오조오억" in word_input: score = 82 # 패륜적 성격이 낮음을 반영

                st.divider()
                st.success("분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 리스크가 높은 단어는 배경 설명을 더 강조
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (고위험 패륜 밈):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경 (사회적 논란 밈):** \n\n {result.get('논란의배경', '')}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
