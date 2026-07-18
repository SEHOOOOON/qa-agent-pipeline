<div align="center">

[![포트폴리오 웹페이지](https://img.shields.io/badge/포트폴리오_웹페이지_보기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/)
[![가상 관제 화면](https://img.shields.io/badge/가상_모의_관제_화면-58A6FF?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)
[![GitHub](https://img.shields.io/badge/GitHub_Repository-181717?style=for-the-badge&logo=github)](https://github.com/SEHOOOOON/qa-agent-pipeline)

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
| **테스트 대상** | **B2B 웹 모의 관제 시스템** | 16대의 장치를 제어하는 가상 관제 대시보드 검증 |
| **검증 전략** | **UI/내부 상태 교차 검증** | Playwright를 통해 화면 표출 상태와 내부 가상 장치 상태를 교차 검증 |
| **단계별 검토** | **QA Checkpoint** | Agent가 결과를 생성하고, 단계별 품질 통제소(Checkpoint)가 기준 미달 산출물을 차단 |
| **파이프라인 연동** | **Pytest / Slack / Notion** | 5가지 원인으로 분류된 테스트 결과를 Slack으로 전송하고 Notion DB에 기록 |

</div>

---

## 🔄 QA 자동화 파이프라인
```text
요구사항과 참고 문서
  ↓
Agent 1 · 요구사항 정제
  ↓ Checkpoint 1 · 요구사항 충분성 검증
Agent 2 · 테스트케이스 설계
  ↓ Checkpoint 2 · TC 품질 적합성 검증
Agent 3 · Playwright 자동화 실행
  ↓ Checkpoint 3 · 실행 결과 신뢰성 검증
Agent 4 · 결과 분석 및 보고
  ↓ Checkpoint 4 · 보고 결과 일관성 검증
Slack 알림 · Notion TC 목록 · 실행 리포트
```

---


## 📂 저장소 구조
```text
qa-agent-pipeline/
├── 📁 docs/                    # 각 Agent별 지시문(프롬프트), 산출물 샘플 및 추적성 매트릭스
├── 📁 tests/                   # Playwright 기반 통합 TC 자동화 스크립트 (test_controller.py 등)
├── 📁 reports/                 # 테스트 자동화 결과 리포트 및 JSON 데이터
├── virtual-controller.html     # 테스트 대상 가상 모의 관제 웹 시스템
├── notify_agent.py             # Slack 및 Notion API 연동 리포팅 봇
└── ARCHITECTURE_TRADEOFFS.md   # 알려진 한계점 및 아키텍처 트레이드오프 회고록
```

---

<div align="center">

*Built with Agentic AI Automation · Playwright · Slack/Notion API*

[![시뮬레이터 바로가기](https://img.shields.io/badge/시뮬레이터_바로가기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

</div>
