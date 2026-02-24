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
                                "너는 글로벌 정책 결정관이야. 아래 3대 원칙을 기계적으로 지켜.\n\n"
                                "1. **점수 하한선 강제 (0점 방지)**:\n"
                                "   - [욕설/비속어]: 반드시 90~100점. '시밤' 같은 변형어도 포함.\n"
                                "   - [문화 이슈]: 반드시 80~89점. '오조오억', '피떡갈비' 등 커뮤니티 밈 포함.\n"
                                "   - [사회적 이슈]: 반드시 70~79점. '마약', '통매음' 등.\n\n"
                                "2. **성적 맥락 오탐 차단**:\n"
                                "   - '시'나 '밤'이 들어간다고 해서 억지로 성적인 의미와 연결하지 마.\n"
                                "   - 확실한 성희롱 단어가 아니라면 [욕설/비속어] 카테고리를 우선해.\n\n"
                                "3. **심층 배경 양식 고정**:\n"
                                "   - 반드시 '어느 커뮤니티에서 유래했는지', '왜 혐오/조롱의 맥락으로 변질됐는지'를 구체적으로 포함해.\n"
                                "   - 분석 근거에 한국어 욕설 발음 유사성 언급을 절대 금지해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [핵심 로직] 시스템 레벨에서 점수 하한선 강제 보정
                score = result.get('부정점수', 0)
                cat = result.get('카테고리', '일상어')
                
                if cat == '욕설/비속어' and score < 90: score = 90
                elif cat == '문화 이슈' and score < 80: score = 85 # 0점 방지
                
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {cat}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 배경 설명 UI 강화 (80점 이상은 무조건 에러 메시지로 강조)
                if score >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경 (커뮤니티 심층 분석):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception as e:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
