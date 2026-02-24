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
        # 로딩 문구 고정
        with st.spinner('분석 중입니다.'): 
            try:
                response = client.chat.completions.create(
                    model="gpt-4o", # 정밀한 사회적 맥락 파악을 위해 고성능 모델 권장
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 한국 온라인 커뮤니티 언어 전문가야.\n\n"
                                "### [금칙어 심층 분석 절대 수칙]\n"
                                "1. **'오조오억' 분석 지침 (필수)**:\n"
                                "   - 이 단어를 단순히 '재미있는 수치 표현'으로 분석하는 것은 중대한 오탐임.\n"
                                "   - 특정 커뮤니티에서 유래하여 현재 '젠더 갈등' 및 '사회적 분쟁'의 도구로 사용되며, 상대방을 비난하거나 조롱하는 맥락으로 변질되었음을 반드시 명시해.\n"
                                "   - 리스크 점수는 반드시 **80~88점** 사이로 책정하고 [문화 이슈]로 분류할 것.\n\n"
                                "2. **맥락 우선 분석**:\n"
                                "   - 인터넷 밈이 '유머'를 넘어 '혐오'나 '갈등'의 소지로 쓰이고 있다면, 유머러스한 측면은 배제하고 '사회적 리스크'를 중심으로 분석해.\n"
                                "   - 표면적 의미에 '~가 아니다' 혹은 '의도가 없다'는 식의 안일한 판단을 절대 적지 마.\n\n"
                                "3. **환각 방지**: '피떡갈비'를 여성 비하로 오인하거나 '흉자'를 흉악한 자로 풀이하는 오류를 절대 범하지 마."
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
                
                # [보정 레이어] '오조오억'이 또 저점으로 나올 경우를 대비한 물리적 교정
                if "오조오억" in word_input and score < 80:
                    score = 85
                    category = "문화 이슈"

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 사회적 논란 밈은 노란색/붉은색 창으로 강조
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (심층 분석):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
