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
        with st.spinner('분석 중입니다.'): 
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이야. 신조어나 밈(Meme) 분석 시 아래 '심층 맥락 우선 원칙'을 적용해.\n\n"
                                "1. **신조어 및 밈 리스크 판정**:\n"
                                "   - 표면적으로 무해해 보이는 의성어(예: 웅앵웅)나 관용구(예: 오조오억)라도, 특정 커뮤니티에서 '조롱'이나 '비하'의 목적으로 사용된다면 반드시 **[문화 이슈]** 카테고리로 분류해.\n"
                                "   - [문화 이슈] 등급의 점수 가이드:\n"
                                "     * 고인 모독/반인륜적 비하 (운지 등): **88~92점**\n"
                                "     * 젠더 갈등/집단 조롱 밈 (오조오억, 웅앵웅 등): **80~85점**\n\n"
                                "2. **설명 작성 지침**:\n"
                                "   - [상세 맥락]: 단어가 가진 표면적 귀여움에 속지 말고, 실제 온라인 상에서 유발하는 갈등과 부정적 인식을 구체적으로 서술해.\n"
                                "   - [판단 근거]: '무해한 표현'이라는 단정적 표현을 지양하고, 커뮤니티 내 사용 빈도와 사회적 민감도를 고려해 제언해.\n\n"
                                "3. **로직 보호**: 카테고리가 '문화 이슈'임에도 점수가 0점으로 나가는 논리적 오류를 절대 범하지 마."
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
                
                # [범용 보정 로직] 단어에 상관없이 '논란성 밈'으로 감지되면 점수 하한선 강제 적용
                # AI가 '웅앵웅'을 일상어로 잘못 판단하더라도, 분석 내용에 '조롱' 키워드가 있다면 보정
                if ("조롱" in result.get('논란의배경', '') or "비하" in result.get('논란의배경', '')) and score < 80:
                    score = 80
                    category = "문화 이슈"

                st.divider()
                st.success("분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (고위험 패륜 밈):** \n\n {result.get('논란의배경', '')}")
                elif score >= 80:
                    st.warning(f"⚠️ **상세 맥락 및 배경 (사회적 논란 밈):** \n\n {result.get('논란의배경', '')}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경 (일반 표현):** \n\n {result.get('논란의배경', '')}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
