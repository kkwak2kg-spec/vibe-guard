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
        with st.spinner('실시간 문맥 및 유해 수위 분석 중...'): 
            try:
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이자 언어학 전문가야. 아래 '5단계 리스크 등급'을 엄격히 적용해.\n\n"
                                "### [리스크 등급 가이드라인]\n"
                                "1. **Level 5 (90~100점)**: 원색적 욕설 원형, 반인륜적 고인 모독, 극도의 혐오 표현.\n"
                                "2. **Level 4 (80~89점)**: 특정 집단/성별에 대한 강한 혐오 및 비하 밈.\n"
                                "3. **Level 3 (60~79점)**: 욕설의 변형어(순화어) 및 타인을 강하게 공격하는 비속어.\n"
                                "4. **Level 2 (40~59점)**: '머저리', '등신' 등 지능이나 행동을 낮잡아 보는 경미한 비하 표현.\n"
                                "5. **Level 1 (0~39점)**: '비아냥', '메롱', '가즈아' 등 일상적 유머, 태도 묘사, 단순 감탄사.\n\n"
                                "### [분석 수칙]\n"
                                "- 한자 풀이 등 사전적 정의보다 '실제 타격감'과 '모욕의 강도'를 우선해.\n"
                                "- 배경 설명에 '공격성 수준'과 '사용 맥락'을 구체적으로 기술해.\n"
                                "- 부정형(~가 아니다) 표현을 지양하고 직설적으로 정의해."
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

                # [지능형 점수 보정 레이어]
                # 1. 원색적 욕설 감지 시 고득점 보장
                if any(k in bg_desc for k in ["원색적", "직설적 욕설"]) and score < 95:
                    score = 95
                    category = "욕설/비속어"
                
                # 2. 경미한 비하 및 일상어 보정 (머저리, 비아냥 등 대응)
                if any(k in bg_desc for k in ["낮잡아", "경미한", "어리석은"]):
                    if score > 60: score = 50 # 머저리 급 보정
                if any(k in bg_desc for k in ["태도", "비꼬는", "일상적", "유머"]):
                    if score > 40: score = 25 # 비아냥 급 보정

                st.divider()
                st.success("심층 분석 완료")
                
                # 리스크 게이지 시각화 추가
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.metric("리스크 점수", f"{score}점")
                with c2:
                    st.subheader(f"🏷️ {category}")
                
                # 점수 구간에 따른 위험도 표시
                if score >= 90:
                    st.progress(score/100); st.error("🚨 최상위 위험: 즉각적인 제재 권장")
                elif score >= 70:
                    st.progress(score/100); st.warning("⚠️ 고위험: 주의 깊은 모니터링 필요")
                elif score >= 40:
                    st.progress(score/100); st.info("ℹ️ 중위험: 일반적인 비하 표현")
                else:
                    st.progress(score/100); st.success("✅ 저위험: 일상적 또는 경미한 표현")

                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                st.write(f"⚠️ **상세 맥락 및 배경:** \n\n {bg_desc}")
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
else:
    st.info("왼쪽 사이드바 또는 상단에 OpenAI API Key를 입력해주세요.")
