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
                                "너는 글로벌 정책 결정관이자 한국 온라인 커뮤니티 전문가야. "
                                "단어 분석 시 '사전적 의미'보다 '커뮤니티 내 실제 조롱/비하 맥락'을 1순위로 판단해.\n\n"
                                "1. **리스크 판정 로직 (전반적 개선)**:\n"
                                "   - [고인 모독/반인륜적 조롱]: 무조건 88~95점.\n"
                                "   - [특정 집단/성별 비하 및 혐오 밈]: 무조건 80~87점. 사전적 의미가 무해해 보여도 실제 사용 의도가 공격적이면 이 구간을 적용해.\n"
                                "   - [단순 욕설 변형]: 70~80점.\n\n"
                                "2. **설명 작성 지침**:\n"
                                "   - [표면적 의미]: 한자 풀이나 단순 의성어 풀이 금지. '실제로 어떤 대상을 비하하기 위해 쓰이는가'를 기재해.\n"
                                "   - [상세 맥락]: 유래된 커뮤니티와 그로 인해 발생하는 사회적 갈등을 아주 구체적으로 서술해.\n\n"
                                "3. **환각 방지**: '밤', '불', '흉악' 등 단어의 일부 글자에 꽂혀서 소설을 쓰지 마. 실제 인터넷 밈 백과사전적 근거를 바탕으로 분석해."
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
                background = result.get('논란의배경', '')
                
                # [범용 보정 로직] 단어 명시 없이 '비하/조롱' 의도가 감지되면 점수 하한선 강제 적용
                # AI가 설명을 '조롱'으로 썼는데 점수를 낮게 준 경우를 자동 교정함
                if any(k in background for k in ["조롱", "비하", "혐오", "모독", "갈등"]):
                    if score < 80:
                        score = 82
                        category = "문화 이슈"
                
                st.divider()
                st.success("분석 완료")
                c1, c2 = st.columns(2)
                with c1: st.metric("리스크 점수", f"{score}점")
                with c2: st.subheader(f"🏷️ {category}")
                
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '한국어')}")
                st.info(f"📖 **표면적 의미:** \n\n {result.get('표면적의미', '')}")
                
                # 심각도에 따른 시각적 UI 분리
                if score >= 88:
                    st.error(f"⚠️ **상세 맥락 및 배경 (고위험 혐오/모독 밈):** \n\n {background}")
                elif score >= 80:
                    st.warning(f"⚠️ **상세 맥락 및 배경 (사회적 논란/비하 밈):** \n\n {background}")
                else:
                    st.info(f"💡 **상세 맥락 및 배경:** \n\n {background}")
                    
                st.info(f"⚖️ **정책 판단 근거:** \n\n {result.get('판단근거', '')}")
                
            except Exception:
                st.error("분석 중 오류 발생")
else:
    st.info("API 키를 입력해주세요.")
