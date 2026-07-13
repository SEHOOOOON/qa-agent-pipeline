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

## 이 프로젝트를 만든 이유

중앙제어 시스템 QA를 수행하면서 같은 요구사항도 검토자의 경험과 관점에 따라 테스트 범위가 달라지고, 머릿속에 있는 판단 기준을 매번 문서와 테스트케이스에 다시 풀어내야 하는 문제를 반복해서 경험했습니다.

AI를 활용하면 테스트케이스를 빠르게 만들 수 있었지만, 요구사항에 없는 색상·문구·상태값까지 그럴듯하게 확정하거나, 정보가 부족한 항목을 정상적인 Pass/Fail 기준처럼 작성하는 문제가 생겼습니다. 단순히 Agent 수를 늘리거나 TC 생성량을 높이는 방식으로는 제가 원하는 QA 품질을 유지하기 어렵다고 판단했습니다.

그래서 이 프로젝트는 **개인의 QA 경험을 대신하는 AI**가 아니라, 제가 중요하게 생각하는 QA 판단 기준을 명시적으로 구조화하고 반복 적용하기 위해 시작했습니다. 각 Agent가 결과물을 생성하되, 단계별 `QA Checkpoint`가 근거·명확성·실행 가능성·보고 일관성을 확인하고, 기준을 충족한 결과만 다음 단계로 전달하도록 설계했습니다.

> **프로젝트 목표:** 요구사항 정제부터 테스트 설계, 자동화 실행과 결과 보고까지 동일한 QA 기준이 끊기지 않도록 연결하고, AI의 추측이 다음 결과물로 전파되는 것을 구조적으로 줄이는 것

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
├── 📁 docs/                    # 각 Agent별 지시문(프롬프트) 및 산출물 샘플
├── 📁 tests/                   # Playwright 기반 E2E 자동화 스크립트 (test_controller.py 등)
├── 📁 reports/                 # 테스트 자동화 결과 리포트 (qa_results.json 등)
├── virtual-controller.html     # 테스트 대상 가상 웹 애플리케이션
└── notify_agent.py             # Slack 및 Notion API 연동 리포팅 봇
```

---

<div align="center">

*Built with Agentic AI Automation · Playwright · Slack/Notion API*

[![시뮬레이터 바로가기](https://img.shields.io/badge/시뮬레이터_바로가기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

</div>
