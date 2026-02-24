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
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 게임 정책 결정관이자 다국어 분석 전문가야. "
                                "단어의 유해성을 판단할 때 아래 '엄격 정책 가이드'를 절대 준수해.\n\n"
                                "### [패륜 및 고수위 비하어 특수 정책]\n"
                                "1. **점수 가이드라인 상향**: 어머니나 가족을 성적으로 모욕하는 패륜적 비하어(예: allerniquersamère 등)는 "
                                "단순 비하를 넘어선 반인륜적 표현으로 간주하여 반드시 **85-95점**을 부여해.\n"
                                "2. **맥락 오염 금지 (중요)**: 외국어 분석 시, 한국어 욕설과 발음이 비슷하다는 내용을 **정책 판단 근거에 절대로 언급하지 마.** "
                                "오직 해당 언어권 내에서의 공격성과 반인륜적 모욕 수위에만 집중해.\n"
                                "3. **카테고리**: 패륜적 표현은 [욕설/비속어] 카테고리로 고정하고, 운영자가 심각성을 즉각 인지하도록 기술해.\n"
                                "4. **상세 배경 의무화**: 단어가 사용되는 상황과 그로 인한 커뮤니티 정서 파괴 수준을 구체적으로 서술해."
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
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{result['부정점수']}점")
                with c2: st.subheader(f"🏷️ {result['카테고리']}")
                
                st.write(f"🌐 **감지된 언어:** {result['언어']}")
                st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                
                # 85점 이상의 고위험 단어는 강력한 경고 UI로 출력
                if result['부정점수'] >= 85:
                    st.error(f"⚠️ **심각한 맥락 및 배경 (고위험 패륜 표현):** \n\n {result['논란의배경']}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
