import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="Global Vibe Guard Pro", page_icon="🌍")
st.title("🌍 글로벌 금칙어 정책 분석기")

if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if api_key:
    client = OpenAI(api_key=api_key)
    word_input = st.text_input("분석할 단어:", placeholder="").strip()

    if st.button("분석"):
        with st.spinner('분석 중입니다.'):
            try:
                # [개선 로직] AI에게 자유도를 주지 않고 '점수 구간'을 강제함
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "너는 글로벌 정책 결정관이야. 아래 '점수 구간 규칙'을 절대 준수해.\n\n"
                                "1. 카테고리 판별 후 점수 부여:\n"
                                "- [욕설/선정적]: 90~100점 사이에서만 부여.\n"
                                "- [문화 이슈/비하 밈]: 80~89점 사이에서만 부여.\n"
                                "- [사회적 이슈/범죄]: 70~79점 사이에서만 부여.\n"
                                "- [정치 이슈/실명]: 60~69점 사이에서만 부여.\n"
                                "- [일상어/신조어]: 0~20점 사이에서만 부여.\n\n"
                                "2. 설명 작성 규칙:\n"
                                "- 욕설 분석 시 '역사', '정치', '음식' 언급 절대 금지.\n"
                                "- 역사적 비하어 분석 시 '성적', '선정적' 언급 절대 금지.\n"
                                "- 각 카테고리의 독립적인 방어 논리를 유지하라."
                            )
                        },
                        {"role": "user", "content": f"단어 '{word_input}'를 위 규칙에 따라 분석해 JSON으로 출력해."}
                    ],
                    response_format={ "type": "json_object" },
                    temperature=0 
                )
                result = json.loads(response.choices[0].message.content)
                
                # UI 출력 부분
                st.divider()
                st.success("분석 완료")
                c1, c2 = st.columns(2)
                c1.metric("리스크 점수", f"{result['부정점수']}점")
                c2.subheader(f"🏷️ {result['카테고리']}")
                st.write(f"🌐 **감지된 언어:** {result.get('언어', '알 수 없음')}")
                st.info(f"📖 **의미:** {result.get('표면적의미', '내용 없음')}")
                
                # 점수에 따른 시각적 경고 수위 조절
                if result['부정점수'] >= 80:
                    st.error(f"⚠️ **배경:** {result.get('논란의배경', '내용 없음')}")
                else:
                    st.warning(f"⚠️ **배경:** {result.get('논란의배경', '내용 없음')}")
                    
            except Exception as e:
                st.error(f"분석 중 오류 발생: {str(e)}")
else:
    st.info("API 키를 입력해주세요.")
