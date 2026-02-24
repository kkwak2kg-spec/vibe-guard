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
                    model="gpt-4o", 
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 대한민국 온라인 커뮤니티의 언어 변화와 혐오 표현을 추적하는 최고 분석관이야. "
                                "사전적 한자 풀이나 단순 의성어 해석은 실제 언어 생활을 반영하지 못하는 '오탐'으로 간주한다.\n\n"
                                "### [금칙어 심층 분석 프로토콜]\n"
                                "1. **'흉자' 분석 지침**: '흉악한 자'라는 사전적 풀이는 100% 오답임. 특정 커뮤니티에서 '가부장제에 순응하는 여성(흉내 내는 자)'을 공격하기 위해 사용하는 '여성 혐오적' 맥락을 반드시 기재할 것.\n"
                                "2. **맥락 우선 원칙**: 단어가 일상적 의미와 비하적 의미를 동시에 가질 경우, 반드시 '비하적/조롱적 의미'를 표면적 의미로 채택해라.\n"
                                "3. **점수 및 카테고리**: 특정 집단이나 성별을 겨냥한 비하/조롱 밈은 반드시 **85점 이상**을 부여하고 [비하/조롱 밈]으로 분류해라.\n"
                                "4. **표면적 의미**: '흉악한' 같은 단어는 절대 포함하지 말고, 실제 혐오 표현으로서의 정의만 명확히 기술해라."
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
                
                # [강제 보정 레이어] '흉자'의 사전적 풀이가 포함될 경우 물리적으로 내용 교체
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
                # 여성 혐오적 맥락이 강하므로 에러 UI로 강조
                st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
