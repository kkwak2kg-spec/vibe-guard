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
                                "너는 글로벌 게임 정책 결정관이야. 아래 지침을 기계적으로 준수해.\n\n"
                                "1. **카테고리 고정**: [욕설/비속어, 선정적, 문화 이슈, 사회적 이슈, 정치 이슈, 일상어] 중 하나를 선택해.\n"
                                "2. **점수 강제 가이드**: 카테고리에 맞춰 반드시 다음 범위 내에서 점수를 생성해.\n"
                                "   - 욕설/선정적: 90-100점\n"
                                "   - 문화 이슈 (오조오억, 피떡갈비 등): 80-89점\n"
                                "   - 사회적 이슈 (마약, 통매음 등): 70-79점\n"
                                "   - 정치 이슈: 60-69점\n"
                                "   - 일상어: 0-20점\n"
                                "3. **절대 금지**: 설명에 한국어 욕설 발음 유사성을 언급하지 마."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [보정 로직 추가] AI가 점수를 0점으로 줬을 경우 카테고리에 맞춰 강제 교정
                final_score = result.get('부정점수', 0)
                category = result.get('카테고리', '일상어')
                
                if category in ['욕설/비속어', '선정적'] and final_score < 90: final_score = 90
                elif category == '문화 이슈' and final_score < 80: final_score = 80
                elif category == '사회적 이슈' and final_score < 70: final_score = 70
                
                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{final_score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result['언어']}")
                st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                
                if final_score >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
