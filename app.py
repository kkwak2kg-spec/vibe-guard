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
        with st.spinner('커뮤니티 심층 맥락을 분석 중입니다.'):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 게임 정책 결정관이자 한국 온라인 커뮤니티 전문가야. "
                                "단순 요약이 아닌, 단어의 '뿌리'와 '변질된 맥락'을 파헤쳐야 해.\n\n"
                                "1. **상세 맥락 및 배경 작성 규칙 (필수)**:\n"
                                "   - 해당 단어가 어떤 특정 커뮤니티에서 유래되었는지 명시해.\n"
                                "   - 표면적 의미 뒤에 숨겨진 '혐오 밈', '조롱 의도', '젠더 갈등' 등의 사회적 논란을 아주 구체적으로 서술해.\n"
                                "   - 왜 이 표현이 일반 유저들에게 불쾌감을 주는지 그 이유를 상세히 기술해.\n\n"
                                "2. **카테고리별 점수 강제 가이드**:\n"
                                "   - [문화 이슈/비하 밈] (오조오억 등): 반드시 80-89점. 절대 0점을 주지 마.\n"
                                "   - [욕설/선정적]: 반드시 90-100점.\n"
                                "   - [일상어]: 0-20점.\n\n"
                                "3. **절대 금지**: 분석 근거에 '한국어 욕설과 발음이 유사하다'는 내용을 억지로 끼워 넣지 마.\n"
                                "4. **맥락 격리**: 이전 단어의 분석 내용을 현재 결과에 섞지 마."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [보정 로직] 0점 방지 및 카테고리 동기화
                final_score = result.get('부정점수', 0)
                category = result.get('카테고리', '일상어')
                if category == '문화 이슈' and final_score < 80: final_score = 85
                elif category == '욕설/비속어' and final_score < 90: final_score = 90

                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{final_score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result['언어']}")
                st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                
                # 상세 배경 출력 (에러 창으로 강조)
                st.error(f"⚠️ **상세 맥락 및 배경 (커뮤니티 심층 분석):** \n\n {result['논란의배경']}")
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
