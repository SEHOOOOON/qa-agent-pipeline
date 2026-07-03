<div align="center">

[![Portfolio](https://img.shields.io/badge/포트폴리오_보기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)
[![GitHub](https://img.shields.io/badge/GitHub-SEHOOOOON-181717?style=for-the-badge&logo=github)](https://github.com/SEHOOOOON)

**Multi-Agent 기반 QA 자동화 파이프라인**  
기획서 분석부터 테스트 시나리오 설계, UI 자동화 테스트, 결함 리포팅까지  
QA 전 과정을 5개의 특화된 AI 에이전트로 자동화한 프로젝트입니다.

</div>

---

## 👨‍💻 경력 요약
> 💡 *상세 경력은 아래 표에 직접 채워주시면 됩니다.*

| 기간 | 회사 | 직책 | 주요 성과 |
|------|------|------|-----------|
| 202X.XX–현재 | [회사명 입력] | [직책 입력] | [핵심 성과 1~2줄 요약] |
| 202X.XX–202X.XX | [회사명 입력] | [직책 입력] | [핵심 성과 1~2줄 요약] |
| 202X.XX–202X.XX | [회사명 입력] | [직책 입력] | [핵심 성과 1~2줄 요약] |

---

## 💡 기획 배경
> **"QA 엔지니어의 개인화된 판단 기준을 AI 에이전트 파이프라인에 녹여내어, 언제나 일관된 품질 거버넌스를 유지할 수 있을까?"**

실무에서 QA 업무는 사람의 판단과 경험에 크게 의존합니다. 동일한 기획서라도 담당자마다 테스트 범위와 결함 판단 기준이 달라지는 문제를 자주 겪었습니다. 
이를 해결하기 위해 제가 실무에서 가장 중요하게 생각하는 '테스트 설계 기준'과 '결함 판정 논리'를 바탕으로, **휴먼 에러 없이 항상 일관된 기준으로 동작하는 자동화 파이프라인**을 구축하고자 본 프로젝트를 시작했습니다.

---

## 📊 핵심 성과
<div align="center">

| 항목 | 상세 | 설명 |
|------|------|------|
| **테스트 대상** | **B2B 웹 관제 시스템** | 16대의 장치를 제어하는 가상 관제 대시보드 검증 |
| **적용 기술** | **Playwright, Python** | 프론트엔드 UI 조작 및 E2E 테스트 시나리오 자동 검증 |
| **자동화 구조** | **5 Multi-Agent** | 5개의 특화 LLM 에이전트가 각 단계별 QA 업무 수행 |
| **업무 연동** | **Slack / Notion API** | 테스트 결과를 실시간 메신저 알림 및 노션 DB에 자동 기록 |

</div>

---

## 🔄 QA 자동화 파이프라인
```text
기획서 및 요구사항 입력
     ↓
[Agent 1] 기획서 분석 및 예외 케이스 도출
     ↓  (Gate 1: 정보 누락 및 모호성 검증 통과)
[Agent 2] 분석된 스펙 기반 테스트 케이스(TC) 설계
     ↓  (Gate 2: Sub-Agent를 통한 TC 논리 오류 사전 검증)
[Agent 3] Playwright 기반 UI 테스트 자동 실행
     ↓  (Gate 3: H/W 네트워크 지연과 S/W 결함 자동 분류)
[Agent 4] 테스트 결과 분석 및 Slack/Notion 자동 리포팅
     ↓
결함 추적 및 테스트 자동화 파이프라인 사이클 완료
```

---


## 📂 저장소 구조
```text
qa-agent-pipeline/
├── 📁 prompts/                 # 각 Agent별 핵심 프롬프트(지시문) 저장소
├── 📁 outputs/                 # Agent가 생성한 TC 및 분석 결과 산출물
├── virtual-controller.html     # 테스트 대상 가상 웹 애플리케이션
├── main.py                     # Multi-Agent 전체 오케스트레이션 엔진
├── test_controller.py          # Playwright 기반 E2E 자동화 스크립트
├── conftest.py                 # Pytest 환경 및 커스텀 리포팅 설정 파일
└── notify_agent.py             # Slack 및 Notion API 연동 리포팅 봇
```

---

<div align="center">

*Built with Agentic AI Automation · Playwright · Slack/Notion API*

[![시뮬레이터 바로가기](https://img.shields.io/badge/시뮬레이터_바로가기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

</div>
