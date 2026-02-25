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
                                "너는 글로벌 정책 결정관이야. 아래 '유해 수위별 점수 정책'을 절대 엄수해.\n\n"
                                "1. **원형 욕설 (Pure Profanity)**:\n"
                                "   - '씨발', '개새끼' 등 변형되지 않은 직접적인 욕설은 반드시 **95~100점**을 부여하고 [욕설/비속어] 카테고리로 분류해.\n\n"
                                "2. **사회적 혐오/비하 밈**:\n"
                                "   - 고인 모독(운지 등)은 **90점 이상**, 젠더/집단 비하(흉자 등)는 **82~88점**을 부여해.\n\n"
                                "3. **변형 비속어 및 일반 밈**:\n"
                                "   - 비속어의 발음 변형(시밤, 시불 등)은 **70~80점** 사이를 유지해.\n"
                                "   - '가즈아', '메롱' 등 일상 유머 밈은 **20~40점**으로 낮게 책정해.\n\n"
                                "4. **분석 지침**: 사전적 의미보다 온라인상의 '실제 타격감'과 '유해성'을 기준으로 점수를 산정해. 절대 원형 욕설을 변형어로 오판하지 마."
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

                # [보정 레이어] 원형 욕설 및 일반 밈 점수 보호
                # 분석 내용에 '원색적', '직설적 욕설' 키워드가 있다면 95점 강제
                if any(k in bg_desc for k in ["원색적", "직설적", "원형 욕설"]) and score < 95:
                    score = 95
                    category = "욕설/비속어"
                
                # 가벼운 유머 키워드 감지 시 하향 유지
                if any(k in bg_desc for k in ["응원", "가벼운", "유희"]) and score >= 70:
                    score = 30
                    category = "일상어/유머 밈"

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                if score >= 90:
                    st.error(f"⚠️ **상세 맥락 및 배경 (최상위 유해성):** \n\n {bg_desc}")
                elif score >= 70:
                    st.warning(f"⚠️ **상세 맥락 및 배경 (주의 필요):** \n\n {bg_desc}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경:** \n\n {bg_desc}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
