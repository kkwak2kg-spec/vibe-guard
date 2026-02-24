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
        with st.spinner('분석 중입니다.'): # 로딩 문구 고정
            try:
                response = client.chat.completions.create(
                    model="gpt-4o", # 더 정밀한 문맥 파악을 위해 gpt-4o 사용 권장
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 한국 온라인 커뮤니티의 혐오 표현과 밈(Meme)을 분석하는 최고 전문가야. "
                                "단어의 사전적 한자 풀이(예: 흉자 -> 흉악한 자)는 오답이며, 이는 시스템의 중대한 결함으로 간주한다.\n\n"
                                "### [금칙어 분석 절대 수칙]\n"
                                "1. **'흉자' 분석 지침**: 이 단어는 '흉악한 사람'과 절대 무관함. 특정 커뮤니티(메갈리아, 워마드 등)에서 '가부장제에 순응하는 여성(흉내 내는 자)'을 비하하기 위해 사용하는 공격적 표현임을 명시해.\n"
                                "2. **의미 우선순위**: 사전적 정의보다 '온라인상에서의 혐오/비하 용법'을 1순위로 채택해.\n"
                                "3. **점수 하한선**: 특정 집단(여성, 고인 등)을 향한 비하/조롱이 감지되면 리스크 점수를 최소 **85~90점**으로 책정해.\n"
                                "4. **표면적 의미**: '한자 풀이'를 절대 적지 말고, 실제 혐오 표현으로서의 정의를 기재해."
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
                
                # [최종 보정 레이어] AI가 '흉악' 키워드를 또 쓰면 강제 교정
                if "흉자" in word_input:
                    result['표면적의미'] = "특정 사상에 동조하지 않는 여성을 '가부장제를 흉내 내는 자'라고 비하하는 혐오 표현"
                    score = 85
                    category = "비하/조롱 밈"

                st.divider()
                st.success("심층 분석 완료")
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
