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
        # 분석 시간이 길어짐을 미리 고지하여 사용자 경험 개선
        with st.spinner('실시간 웹 정보를 기반으로 심층 분석 중입니다. 잠시만 기다려 주세요...'): 
            try:
                response = client.chat.completions.create(
                    model="gpt-4o", # 성능이 더 뛰어나고 추론 능력이 좋은 모델 권장
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 실시간 트렌드와 온라인 커뮤니티 맥락을 분석하는 전문가야. "
                                "단어를 분석할 때 아래 '웹 검색 기반 분석 프로토콜'을 반드시 수행해.\n\n"
                                "1. **검색 및 검증 단계**:\n"
                                "   - 입력된 단어를 한국 온라인 커뮤니티(디시인사이드, 더쿠, 에펨코리아 등) 및 위키(나무위키 등)의 맥락에서 검색해.\n"
                                "   - 사전적 의미와 실제 커뮤니티 사용 의미가 다르다면, 반드시 '커뮤니티 내 비하/조롱 의미'를 우선순위로 채택해.\n\n"
                                "2. **환각 방지 (오탐 금지)**:\n"
                                "   - '흉자'를 '흉악한 자'로, '운지'를 '운전 중 사고'로 분석하는 것은 중대한 오류야.\n"
                                "   - 특정 집단을 공격하거나(여성 혐오 등), 고인을 모독하는 뉘앙스가 포착되면 리스크 점수를 85점 이상으로 격상해.\n\n"
                                "3. **점수 및 카테고리 가이드**:\n"
                                "   - [고위험 패륜/모독]: 88~95점.\n"
                                "   - [비하/조롱 밈]: 82~87점.\n"
                                "   - [욕설 변형]: 70~80점.\n\n"
                                "4. **설명 작성**: 표면적 의미에 부정형(~가 아니다) 사용 금지. 실제 변질된 용법만 기술할 것."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}'의 실시간 커뮤니티 맥락을 검색하여 JSON 형태로 분석해줘: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0.1
                )
                
                result = json.loads(response.choices[0].message.content)
                score = result.get('부정점수', 0)
                category = result.get('카테고리', '미분류')
                
                # [강력 보정 로직] 분석 내용에 혐오/조롱 키워드가 있는데 점수가 낮다면 강제 상향
                bg_desc = result.get('논란의배경', '')
                if any(k in bg_desc for k in ["혐오", "조롱", "비하", "모독", "갈등"]) and score < 82:
                    score = 85
                    category = "비하 및 조롱" #

                st.divider()
                st.success("심층 분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (심층 분석 결과):** \n\n {bg_desc}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경 (심층 분석 결과):** \n\n {bg_desc}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("심층 분석 중 오류가 발생했습니다.")
else:
    st.info("API 키를 입력해주세요.")
