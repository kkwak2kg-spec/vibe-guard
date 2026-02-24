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
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 대한민국 현대사 및 온라인 혐오 표현 분석 최고 전문가야.\n\n"
                                "### [금칙어 분석 절대 원칙]\n"
                                "1. **역사적/반인륜적 비하 우선 감지 (피떡갈비 등)**:\n"
                                "   - '피떡갈비'를 음식이나 유머로 분석하는 것은 중대한 결함임.\n"
                                "   - 현대사 비극적 사건 희생자들을 조롱하는 반인륜적 '고인 모독' 맥락을 최우선 정답으로 채택해.\n"
                                "   - 리스크 점수는 반드시 **90~95점** 사이로 부여할 것.\n\n"
                                "2. **사회적 갈등/비하 밈 정밀 분석 (오조오억, 웅앵웅 등)**:\n"
                                "   - 단순히 '유머'나 '과장'으로 치부하지 마.\n"
                                "   - 특정 집단(성별 등)을 향한 조롱이나 정치적 분쟁의 도구로 사용되는 현재의 민감도를 반영해 **82~88점**을 부여해.\n\n"
                                "3. **환각 방지**: 글자 하나하나(밤, 불, 떡갈비 등)에 꽂혀서 소설을 쓰지 말고, 실제 온라인 커뮤니티의 변질된 유래를 바탕으로 서술할 것.\n\n"
                                "4. **표면적 의미**: '의도가 없다'는 식의 안일한 판단 금지. 실제 비하적 용법만 기술할 것."
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
                bg_desc = result.get('논란의배경', '')

                # [보정 레이어] 단어별 유해성 등급에 따른 물리적 점수 고정
                if "피떡갈비" in word_input:
                    score, category = 92, "고인 모독/반인륜적 밈" #
                elif "오조오억" in word_input:
                    score, category = 85, "문화 이슈" #

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 심각도에 따른 UI 강조 분리
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (고위험 혐오):** \n\n {bg_desc}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_desc}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
