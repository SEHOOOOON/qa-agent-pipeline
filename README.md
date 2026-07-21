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

## 🔄 QA 자동화 파이프라인 (Data Flow & Checkpoints)

> **💡 핵심 설계 철학**: AI의 환각(Hallucination)과 비결정론적 판단이 다음 단계로 전파되는 것을 막기 위해, 각 Agent의 산출물은 반드시 Checkpoint(CP)를 거치도록 설계했습니다.

```text
1. Agent 1 · 요구사항 정제 
   ➔ 메모리상 requirement_contract 생성
2. Checkpoint 1 · 전달 가능 범위 확정 (모호한 요구사항 차단)
3. Agent 2 · 3-Tier(요구사항/UI/제어) 기준으로 테스트케이스(TC) 생성
4. Checkpoint 2 · TC 품질 및 근거 승인 (V1: 명시적 중복 검토, V2: 의미론적 커버리지 분석)
   --- (여기서부터 자동화 실행 단계) ---
5. Agent 3 Runner 시작 (Pytest)
6. TC-ENV-000 (Pre-check) 실행 ➔ Checkpoint 3 (실행 전 판정: 통과 시 본 테스트 진행)
7. 본 테스트(Product & Injected Scenarios) 실행 ➔ 원본 결과 저장
8. Checkpoint 3 (실행 후 판정) · 제품 판정 가능 여부(VALID / BLOCKED) 기록
9. Agent 4 · 결과 분석 및 "표준 결과 초안(Draft)" 생성 (결함 원인 5가지 분류)
10. Checkpoint 4 · Report/JSON 원본과 Agent 4 초안을 교차 검증 (VALIDATED 처리)
11. 최종 승인 시 `agent4_summary.json` 저장 및 Slack/Notion 전송용 Payload 생성
```

### 🎯 아키텍처 정합성 핵심 검토 사항 (10 Key Considerations)

프로젝트 구현 과정에서 제기된 주요 설계 충돌 이슈를 다음과 같이 정의하고 해결했습니다.

1. **순환 참조 모순 해결 (Agent 4 ↔ Checkpoint 4)**
   - Agent 4가 최종 `agent4_summary.json`을 직접 생성하고 CP4가 이를 검사하면 순환 참조가 발생합니다. 
   - **해결**: Agent 4는 메모리에 **'결과 초안(Draft)'**만 생성하고, CP4가 이 초안을 원본 리포트와 대조하여 통과(VALIDATED)했을 때만 최종 JSON 파일과 Execution/Release 상태를 확정하도록 단방향 데이터 흐름을 강제했습니다.
2. **CP3 BLOCKED 판정 시 원인 분류 로직 확립**
   - CP3에서 환경 이슈로 BLOCKED 판정이 나더라도, 이는 '제품 결함 판정 금지'를 의미할 뿐 에러 데이터가 버려지는 것이 아닙니다. 이 증거는 Agent 4로 전달되어 `automation_issue` 또는 `environment_issue`로 정상 분류됩니다.
3. **Pre-check(TC-ENV-000)의 정확한 위치**
   - 실행 환경을 점검하는 Pre-check는 Agent 3 외부의 별도 모듈이 아니라, Agent 3 Runner(Pytest) 내의 **최우선 실행 Phase**로 동작하여 실패 시 후속 Product TC들의 실행을 중단시킵니다.
4. **TC ID와 Test ID의 분리 매핑**
   - 요구사항과 매핑되는 `TC ID(예: TC-MODE-001)`와 실제 실행되는 자동화 함수인 `Test ID(예: test_tc_mode_001)`는 동일한 문자열일 필요가 없으며, JSON 리포트에서 서로 **정확히 1:1 매핑**되어 상태를 공유하는지 검증합니다.
5. **Requirement Gap (주입 시나리오) 분리**
   - 실제 운영 흐름(Actual)에서는 CP1에서 정보가 부족한 요구사항이 차단되어 Agent 3가 실행하지 않습니다. 
   - 단, 포트폴리오의 통합 런(Run)에서 나타나는 ⚠️ Skipped TC는 Agent 4의 `requirement_review` 로직과 HOLD 정책 작동을 시연하기 위해 의도적으로 주입한(Injected) 검증용 시나리오입니다.
6. **예상 결과 필드의 세분화**
   - 혼동을 막기 위해 시나리오 메타데이터의 결과를 두 개로 분리했습니다. `expected_pytest_status`(Pytest 상의 성공/실패 여부)와 `expected_classification`(최종 결함 원인 분류). Pytest가 Failed로 끝나는 것이 예상된 동작이더라도, 최종 파이프라인 판단은 HOLD가 됩니다.
7. **기능 검증 중복 검사의 범위 한정**
   - 현재 V1 단계의 Checkpoint 2에서는 '동일 ID, 동일 목적, 동일 조건의 명시적 중복'을 검사합니다. 기존 결함 이력을 조회하는 의미론적(Semantic) Coverage Gap 분석은 향후 고도화(V2) 과제로 분리했습니다.
8. **시스템 판정 용어의 통일**
   - 파이프라인의 최종 결과인 `release_decision`은 실무자의 릴리즈 승인 결재가 아니라, 파이프라인 규칙에 따른 **시스템 권고 판정 (System Release Recommendation)** 임을 명확히 정의합니다.
9. **CP4 외부 플랫폼(Slack/Notion) 연동 검증 범위**
   - CP4는 외부 플랫폼의 UI나 DB를 크롤링하여 다시 검증하는 것이 아닙니다. 전송 직전에 생성된 **Payload 수치**가 방금 확정된 Agent 4 Summary 데이터와 일치하는지만 논리적으로 검증합니다.
10. **현재 구현(Current)과 향후 계획(Future)의 명확한 분리**
    - 현재 JSON 기반 리포트 추출 및 CP4 검증은 구현이 완료되었으나, Playwright Trace 파일 수집, 상태 Snapshot 캡처, `evidence_path`의 S3 자동 연동 등은 향후 고도화 목록으로 남겨두어 오버엔지니어링(Over-engineering) 오해를 방지했습니다.

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

## 🚀 Future Works (v2 업데이트 예정)
- **에이전트 1번(요구사항 파싱)의 RAG 기반 자율 엣지케이스 교차 검증 도입**
  - 사내 공통 안전 규격서(Safety Guideline)와 신규 PRD 문서를 교차 검증(Cross-Validation)하여 AI 환각(Hallucination) 없이 엣지케이스(Edge Case) TC를 자동 도출하는 기능 추가 예정.
