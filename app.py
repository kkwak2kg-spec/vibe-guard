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
    api_key = st.sidebar.text_input("OpenAI API Key 설정이 필요합니다", type="password")

if api_key:
    try:
        client = OpenAI(api_key=api_key)
        # 입력창 placeholder 빈칸 유지
        word_input = st.text_input("분석할 단어:", placeholder="")

        if st.button("분석"):
            # 로딩 문구를 '분석 중입니다.'로 간결하게 고정
            with st.spinner('분석 중입니다.'):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system", 
                                "content": (
                                    "너는 글로벌 게임 정책 결정관이자 언어 분석 전문가야. "
                                    "이전 대화의 방어 논리를 현재 분석에 절대 섞지 마라. "
                                    "다음의 '카테고리별 격리 판정 프로토콜'을 기계적으로 준수하여 JSON으로만 답해.\n\n"
                                    
                                    "### [PROTOCOL 1: 욕설 및 선정성]\n"
                                    "- 대상: 씨발, 보빨, chinorri 등 직접적인 욕설이나 성적 비하/행위 암시.\n"
                                    "- 카테고리: '욕설/비속어' 또는 '선정적'으로 분류.\n"
                                    "- 점수: 반드시 **90-100점** 고정.\n"
                                    "- 설명: 언어적 폭력성, 성적 수치심 유발을 중심으로 기술 (정치/일상 언급 절대 금지).\n\n"
                                    
                                    "### [PROTOCOL 2: 정치적 비하 및 혐오 밈]\n"
                                    "- 대상: 윤두창, 이죄명 등 실명 변형어 및 오조오억 등 젠더 갈등 밈.\n"
                                    "- 카테고리: '커뮤니티 논란 밈' 또는 '문화 이슈'.\n"
                                    "- 점수: 반드시 **80-88점** 고정.\n"
                                    "- 설명: 실명과 혐오 단어의 결합 수법 혹은 특정 집단 비하 맥락을 상세 분석.\n\n"
                                    
                                    "### [PROTOCOL 3: 불법 및 사회적 리스크]\n"
                                    "- 대상: 마약, 대포통장 등 범죄 관련.\n"
                                    "- 카테고리: '사회적 이슈'.\n"
                                    "- 점수: 단순 명사는 **75-80점**, 실행 권유(마약먹자 등)는 **85-90점** 고정.\n"
                                    "- 설명: 법적 리스크와 모방 범죄 위험성 중심 기술.\n\n"
                                    
                                    "### [PROTOCOL 4: 실명 및 일상어]\n"
                                    "- 대상: 이승만, 가즈아 등 순수 실명 및 긍정적 유행어.\n"
                                    "- 카테고리: '정치 이슈' 또는 '일상어'.\n"
                                    "- 점수: 실명은 **60-70점**, 일상어는 **10-20점** 고정.\n"
                                    "- 설명: 객관적 인물 정보 또는 긍정적 유래 기술.\n\n"
                                    
                                    "※ 내부 프로토콜 이름(Protocol 1 등)이나 'D' 같은 약어는 결과에 절대 포함하지 마."
                                )
                            },
                            {
                                "role": "user", 
                                "content": f"단어 '{word_input}' 분석 JSON: {{\"언어\": \"\", \"카테고리\": \"\", \"부정점수\": 0, \"표면적의미\": \"\", \"논란의배경\": \"\", \"판단근거\": \"\"}}"
                            }
                        ],
                        response_format={ "type": "json_object" },
                        temperature=0 
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    
                    st.divider()
                    st.success("분석 완료")
                    
                    col_score, col_cat = st.columns(2)
                    with col_score:
                        st.metric("리스크 점수", f"{result['부정점수']}점")
                    with col_cat:
                        st.subheader(f"🏷️ {result['카테고리']}")
                    
                    st.write(f"🌐 **감지된 언어:** {result['언어']}")
                    st.info(f"📖 **표면적 의미:** \n\n {result['표면적의미']}")
                    
                    # 점수에 따른 UI 시각화 차별화
                    if result['부정점수'] >= 80:
                        st.error(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    elif result['부정점수'] >= 40:
                        st.warning(f"⚠️ **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    else:
                        st.info(f"💡 **상세 맥락 및 배경:** \n\n {result['논란의배경']}")
                    
                    st.info(f"⚖️ **정책 판단 근거:** \n\n {result['판단근거']}")
                    
                except Exception as inner_e:
                    st.error(f"분석 중 오류 발생: {inner_e}")
                    
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
else:
    st.info("API 키를 설정해 주세요.")
