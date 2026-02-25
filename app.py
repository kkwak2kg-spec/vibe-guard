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
                                "너는 글로벌 정책 결정관이야. 아래 '리스크 등급 가이드라인'을 절대적으로 준수해.\n\n"
                                "1. **주된 용법(Primary Usage) 판단 원칙**:\n"
                                "   - '가즈아', '메롱', '킹받네' 등 일상적 유머나 응원으로 90% 이상 소비되는 단어는 [일상/유머 밈]으로 분류하고 점수를 **20~40점** 사이로 책정해.\n"
                                "   - 특정 상황에서의 조롱 가능성만으로 점수를 70점 이상 주지 마.\n\n"
                                "2. **유해성 등급 고정**:\n"
                                "   - [고인 모독/반인륜적 밈]: 90~95점. (예: 운지, 피떡갈비 등)\n"
                                "   - [사회적 갈등/비하 밈]: 80~88점. (예: 흉자, 오조오억 등)\n"
                                "   - [비속어 변형]: 70~79점. (예: 시밤, 시불 등)\n\n"
                                "3. **환각 방지**: 한자 풀이나 단어 일부 글자에 집착한 소설 쓰기를 엄금함. 반드시 검증된 온라인 커뮤니티 유래를 바탕으로 작성해.\n\n"
                                "4. **설명 규칙**: 표면적 의미에 부정형(~가 아니다) 사용 금지. 실제 통용되는 용법만 기술해."
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

                # [동적 등급 보정 레이어] 일상적인 밈이 과잉 판정되는 것을 방지
                # 배경 설명에 '응원', '격려', '유머', '가벼운' 등의 키워드가 주를 이루면 점수 하향
                if any(k in bg_desc for k in ["응원", "격려", "유희", "가벼운"]) and score >= 70:
                    score = 35
                    category = "일상어/유머 밈"

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 심각도에 따른 UI 차등화
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (고위험 유해 밈):** \n\n {bg_desc}")
                elif score >= 70:
                    st.warning(f"⚠️ **상세 맥락 및 배경 (주의 필요):** \n\n {bg_desc}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경 (일반 정보):** \n\n {bg_desc}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
