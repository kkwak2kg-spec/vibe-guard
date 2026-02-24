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
                    model="gpt-4o", # 정밀한 역사적 맥락 파악을 위해 고성능 모델 사용
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 한국 현대사/커뮤니티 언어 전문가야.\n\n"
                                "### [금칙어 심층 분석 절대 수칙]\n"
                                "1. **'피떡갈비' 분석 지침 (필수)**:\n"
                                "   - 이 단어는 '여성 비하'나 '신체 부위 조롱'과 전혀 무관함.\n"
                                "   - 실제 정의: 특정 온라인 커뮤니티에서 한국 현대사의 비극적 사건 희생자들의 시신을 잔인하게 묘사하고 조롱하기 위해 사용하는 '고인 모독형' 혐오 표현임.\n"
                                "   - 점수는 반드시 **90~95점** 사이로 설정하고 [고인 모독/반인륜적 밈]으로 분류할 것.\n\n"
                                "2. **맥락 우선순위**:\n"
                                "   - 단어의 글자 조합(예: 피, 갈비, 흉, 밤 등)에 꽂혀서 자의적으로 의미를 날조하는 환각을 절대 경계해.\n"
                                "   - 반드시 실시간 웹 맥락과 커뮤니티 밈 백과사전적 근거를 바탕으로 유래를 기술해.\n\n"
                                "3. **설명 작성 규칙**:\n"
                                "   - [표면적 의미]: 부정형(~가 아니다) 없이 실제 변질된 비하적 정의만 기재할 것.\n"
                                "   - [상세 맥락]: 해당 표현이 유발하는 사회적 분노와 고인에 대한 반인륜적 성격을 구체적으로 서술할 것."
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
                
                # [보정 레이어] '피떡갈비'가 여성 비하로 오탐될 경우를 대비한 물리적 교정
                if "피떡갈비" in word_input:
                    result['표면적의미'] = "현대사 비극적 사건의 희생자들을 잔인하게 비하하고 조롱하는 고인 모독 표현"
                    score = 92
                    category = "고인 모독/반인륜적 밈"

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 반인륜적 혐오는 붉은색 창으로 강력하게 경고
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (심각한 반인륜적 표현):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
