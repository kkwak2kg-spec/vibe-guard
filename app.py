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
                    model="gpt-4o", # 정밀한 문맥 파악을 위해 고성능 모델 사용
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 한국 온라인 커뮤니티 언어 전문가야.\n\n"
                                "### [금칙어 분석 핵심 원칙]\n"
                                "1. **맥락 우선순위 (사전적 의미 배제)**:\n"
                                "   - 단어를 분석할 때 한자 풀이나 사전적 정의보다 '실제 온라인 커뮤니티(디시, 더쿠, 에펨 등)에서의 사용 용법'을 최우선 정답으로 채택해.\n"
                                "   - 특히 신조어의 경우, 겉모습이 무해해 보여도 특정 집단(성별, 고인, 특정 계층)을 비하하는 어원이나 조롱의 의도가 있는지 철저히 파악해.\n\n"
                                "2. **표면적 의미 작성 규칙**:\n"
                                "   - '~가 아니다' 혹은 '~와 무관하다' 같은 부정형 사족은 절대 금지야.\n"
                                "   - 해당 단어의 실제 어원(예: 흉자 -> 흉내자지)과 현재 통용되는 비하적 정의만 직설적으로 기재해.\n\n"
                                "3. **점수 하한선 자동 적용 (0점 방지)**:\n"
                                "   - [고인 모독/반인륜 조롱]: 88~95점.\n"
                                "   - [집단/성별 비하 및 혐오 밈]: 80~87점.\n"
                                "   - 분석 내용에 '비하', '조롱', '혐오' 키워드가 하나라도 포함되면 무조건 80점 이상을 부여해.\n\n"
                                "4. **환각 방지**: 글자 하나하나(밤, 불, 흉 등)에 집착하여 소설을 쓰지 말고, 검증된 커뮤니티 밈의 역사를 바탕으로 서술해."
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

                # [범용 보정 로직] AI가 설명을 조롱으로 썼는데 점수를 낮게 준 경우 시스템이 보정
                if any(k in bg_desc for k in ["조롱", "비하", "혐오", "모독", "갈등"]) and score < 80:
                    score = 82
                    if category == "미분류": category = "비하/조롱 밈"

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 80점 이상 위험어는 붉은색 창으로 강조
                if score >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경 (심층 분석):** \n\n {bg_desc}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_desc}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
