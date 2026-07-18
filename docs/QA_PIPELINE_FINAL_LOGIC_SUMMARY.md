# 🚀 QA 파이프라인 (Agent 1~4 및 Checkpoint 1~4) 최종 로직 및 아키텍처 명세서

본 문서는 프로젝트 진행 과정에서 고도화된 **Agent(실행 주체)**와 **Checkpoint(검증 게이트)**의 역할, 세부 로직, 판정 기준, 그리고 표준화된 용어 체계를 완벽하게 분리하여 정리한 최종 명세서입니다.

---

## 0. 공통 용어 및 상태 표준화 (Terminology Standardization)
파이프라인 전체를 관통하는 핵심 용어들을 다음과 같이 표준화하여 모호성을 제거했습니다.

*   **진행 상태 (Proceed / Hold)**:
    *   `전체 진행(Proceed)`: 모든 항목이 검증을 통과하여 다음 단계로 넘어갈 수 있음.
    *   `일부 진행(Partial Proceed)`: 치명적 결함은 없으나 일부 수정 권고(Warning)가 있어 조건부로 넘어감.
    *   `확인 후 진행(Hold)`: 크리티컬한 결함이나 모호성이 있어 컷오프(차단)됨.
*   **시스템 상태 구분 (상태 격리)**:
    *   `사용자 UI (User UI)`: 화면에 표시되는 시각적 상태 및 피드백.
    *   `내부 장치 상태 (Virtual Register/State)`: 백엔드/시뮬레이터가 실제로 가지고 있는 데이터 상태.
*   **TC 용어 기준**:
    *   단순 기대결과가 아닌 **`기대결과(Expected Result)`**로 용어를 고정.
    *   엔드투엔드 시나리오는 **`통합 테스트(E2E)`**로 명칭 통일.

---

## 1. Agent (실행 주체) 상세 명세

### 🤖 Agent 1: 요구사항 분석 에이전트 (Requirement Analyst)
*   **역할**: 기획서, 요구사항 명세서를 읽고 누락되거나 모호한 기획의 빈틈을 찾아냅니다.
*   **분류 및 판정 기준 (Ambiguity Detection)**:
    *   **정상**: 모든 UI 동작, 에러 피드백이 명시되어 있는 경우.
    *   **모호성 감지 (기획 누락)**: 에러 상황은 정의되었으나, 이에 따른 구체적인 시스템 피드백(예: CH05 에러 발생 시 UI 색상 변화 기준)이 문서에 명확하지 않은 경우 이를 "요구사항 모호성"으로 분류하여 테스트 설계 전 기획자에게 확인을 요청합니다.

### 🤖 Agent 2: TC 설계 에이전트 (TC Designer)
*   **역할**: 확정된 기획을 바탕으로 엣지 케이스와 상태 격리가 포함된 구체적인 TC를 설계합니다.
*   **분류 및 판정 기준**:
    *   **식별자 및 추적성**: 목적 기반 ID 체계(`TC-MODE-001`, `TC-ENV-000`, `TC-INT-002`)를 도입하고, 요구사항 추적 매트릭스에 `CRIT(Criteria)` ID를 연결하여 완벽한 추적성을 보장합니다.
    *   **상태 격리 (State Isolation)**: 하나의 TC가 너무 많은 것을 검증하여 연쇄 실패가 일어나지 않도록, `사용자 UI` 검증과 `내부 장치 상태` 검증을 격리합니다.
    *   **Boundary(경계값) 테스트**: 30°C 초과 조작 시도 등 한계값 도달 시, 시스템 방어 로직(Toast 알림, 롤백)을 필수 검증 항목으로 둡니다.

### 🤖 Agent 3: 자동화 테스트 실행 (Test Executor)
*   **역할**: Agent 2가 설계한 TC를 실제 코드(`test_controller.py`)로 변환하여 시뮬레이터에서 실행하고 원본 데이터를 남깁니다.
*   **핵심 로직 및 기준**:
    *   **Demo 정직성 (Simulator Honesty)**: 시뮬레이터 내부의 응답은 실제 시스템의 피드백을 모사하며, 테스트 패스를 위해 결과를 조작하지 않는 정직한 데모 환경을 유지합니다.
    *   **메타데이터 강제 주입 (`conftest.py`)**: `pytest_html_results_summary` 훅 버그를 수정하여 카운트 정합성을 맞추고, `run_id`, `tc_id`, `executed_at`, `duration`, `evidence_path(스크린샷)`를 필수로 기록합니다.

### 🤖 Agent 4: 결과 분석 및 보고 (Result Reporting Manager)
*   **역할**: 실행된 테스트 결과를 파싱하여, 단순 성공/실패 여부를 넘어 'QA 원인'을 분류하고 최종 의사결정을 내립니다.
*   **QA 원인 분류 기준 (5 Category)**:
    *   `product_defect` (제품 결함): 명확하게 소프트웨어가 스펙대로 동작하지 않음.
    *   `requirement_review` (요구사항 확인 필요): 기획서 기준 미비로 인해 맞고 틀림을 Assert 할 수 없음.
    *   `environment_issue` (환경·시뮬레이터 문제): 제어 명령은 보냈으나 시뮬레이터가 응답하지 않아 Timeout 발생 등.
    *   `automation_issue` (자동화 코드 문제): DOM 요소 변경 등 Playwright 스크립트 에러.
    *   `not_executed` (미실행): 사전 조건 불만족으로 스킵됨.
*   **실행 결과 판정 기준 (`execution_result`)**:
    *   `FAILED`: 원인이 환경(네트워크)이든 결함이든 Failed나 Error가 1건이라도 있으면 무조건 실패. (환경 문제라고 통과시켜주지 않음)
    *   `INCOMPLETE`: 실패는 없으나 Skipped 등이 존재할 경우.
    *   `PASSED`: 100% Passed.
*   **릴리즈 판정 기준 (`release_decision`)**:
    *   `HOLD`: 실행 결과가 FAILED 거나, 실행이 통과했어도 기획 누락(`requirement_review`) 또는 미실행(`not_executed`) 항목이 하나라도 존재하면 배포 반려.
    *   `PASS`: 완전한 통과 및 모호성 제로 상태.

---

## 2. Checkpoint (데이터 검증 게이트) 상세 명세

각 Agent가 다음 단계로 넘어가기 전, 산출물의 데이터 무결성과 품질을 컷오프(Cut-off) 하는 검증 게이트(Reviewer) 역할입니다.

### 🛑 Checkpoint 1: 요구사항 정합성 검증
*   **위치**: Agent 1 -> Agent 2 사이
*   **판정 기준**: 요구사항 명세서 내에 상충되는 룰(예: Rule 2와 모드 변경 규칙의 충돌)이 없는지, 누락된 스펙(모호성)이 해소되었는지 검증합니다. 통과하지 못하면 `HOLD` 처리되어 TC 설계가 불가능합니다.

### 🛑 Checkpoint 2: TC 커버리지 및 추적성 검증 (Cross-Validation)
*   **위치**: Agent 2 -> Agent 3 사이
*   **판정 기준 및 제약 (Reviewer Constraints)**: 
    *   **교차 검증 (Cross-Validation)** 요구: 긍정 케이스(해피 패스)만 있지 않은지, 반드시 네거티브 케이스나 엣지 케이스가 교차 검증되었는지 봅니다.
    *   **추적성**: `TC-ID`가 요구사항의 `CRIT` ID와 1:1 이상으로 완벽히 매핑되었는지 검사합니다.
    *   검증 미달 시 `확인 후 진행(Hold)` 또는 `일부 진행(Partial Proceed)` 판정을 내립니다.

### 🛑 Checkpoint 3: 자동화 스크립트 실행 환경 검증
*   **위치**: Agent 3 실행 직전 (Pre-check)
*   **판정 기준**: 테스트가 실행될 대상 시스템(시뮬레이터) 및 초기 가상 레지스터 상태가 완벽한지 검증(`TC-ENV-000`). 환경 불량으로 인한 가짜 실패(False Negative)를 방지하여 테스트 신뢰도를 보장합니다.

### 🛑 Checkpoint 4: 최종 데이터 무결성 검증 (Data Integrity)
*   **위치**: Agent 4 내부 (외부 리포팅 발송 직전)
*   **판정 기준 및 로직**:
    *   **교차 검증 (JSON vs HTML)**: Agent 3가 만든 `qa_results.json`과 `report.html`의 data-jsonblob을 양방향으로 뜯어, 총 실행 건수, Test ID, 상태(Pass/Fail)가 100% 일치하는지 비교 검사합니다.
    *   **논리 조합 검증 (`ALLOWED_STATUS_CLASSIFICATIONS`)**: Pytest 상태와 QA 분류의 조합이 말이 되는지 검증합니다. (예: `Passed`인데 `product_defect`로 분류되면 불일치 에러 발생)
    *   **결과 판정 (`VALIDATED`)**: 통과 시 테스트 성공을 의미하는 PASS가 아닌, 데이터가 조작되지 않았음을 보증하는 **`VALIDATED`** 상태를 부여합니다.
    *   **차단 룰 (`BLOCKED`)**: 불일치 발생 시(`BLOCKED`) 외부(Slack/Notion)로 테스트 결과를 발송하는 것을 원천 차단하여, 잘못된 데이터가 보고되는 것을 막습니다.
