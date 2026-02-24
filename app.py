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
                                "너는 글로벌 정책 결정관이야. 아래 지침을 기계적으로 준수해.\n\n"
                                "1. **표면적 의미 작성 규칙**:\n"
                                "   - '~와 무관하다'는 등의 부정형 설명은 절대 금지야.\n"
                                "   - 단어가 실제로 무엇을 뜻하는지, 어떤 욕설의 변형인지 실제 의미만 간결하게 기술해.\n\n"
                                "2. **변형어 점수 및 카테고리 고정**:\n"
                                "   - '시불', '시밤' 등 욕설 변형어는 반드시 [욕설/비속어] 카테고리로 분류해.\n"
                                "   - 점수는 절대 0점을 주지 말고, 변형어 가이드에 따라 **70~80점** 사이를 부여해.\n"
                                "   - 원형 욕설(씨발 등)은 반드시 90점 이상을 부여해.\n\n"
                                "3. **배경 분석 강화**:\n"
                                "   - '밤'이나 '불' 같은 글자에 집착하지 말고, 온라인 커뮤니티에서 필터링 우회를 위해 생성된 맥락을 기술해.\n"
                                "   - 정책 근거에 '한국어 욕설 발음 유사성' 언급은 맥락 오염이므로 절대 금지해."
                            )
                        },
                        {"role": "user", "content": f"'{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                
                result = json.loads(response.choices[0].message.content)
                
                # [보정 로직] 변형어 0점 방지 및 자동 점수 할당
                score = result.get('부정점수', 0)
                category = result.get('카테고리', '일상어')
                
                # 비속어로 분류됐는데 점수가 낮을 경우 강제 보정
                if category == '욕설/비속어' and score < 70:
                    score = 75 

                st.divider()
                st.success("분석 완료")
                
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                if score >= 80:
                    st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                else:
                    st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result.get('논란의배경', '')}")
                
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception as e:
                st.error(f"분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
