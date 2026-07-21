# QA_PIPELINE_ARCHITECTURE (구현 기준 문서)

본 문서는 파이프라인의 핵심 설계와 Agent/Checkpoint의 역할, 데이터 흐름, 그리고 상태값 판정 순서를 정의하는 **Single Source of Truth (SSOT)** 구현 기준 문서입니다.

## 1. Agent와 Checkpoint의 역할 분리

파이프라인의 근본 원칙은 다음과 같습니다.
> **"Agent는 만든다. Checkpoint는 검사하고 막는다."**

*   **Agent (실행 주체)**: 새로운 산출물을 생성합니다.
*   **Checkpoint (품질 게이트)**: Agent가 생성한 산출물을 검증하여 다음 단계로 전달해도 되는지 평가합니다. 절대 새로운 데이터를 창조하지 않습니다.

### Agent별 책임
*   **Agent 1**: 정제된 요구사항 생성, 영향 관제점 분석, 테스트 가능 범위 확정. (UI, TC 생성 및 Pass/Fail 판정 **금지**)
*   **Agent 2**: 3-Tier QA 기준(공통/도메인/기능)을 적용하여 테스트케이스(TC) 생성.
*   **Agent 3**: 승인된 TC와 매핑된 Playwright 자동화 테스트 실행 및 증거(로그, 상태) 기록. (TC를 코드로 변환하는 로직 **없음**)
*   **Agent 4**: 5가지 QA 원인 분류 및 표준 결과 초안 생성.

### Checkpoint별 책임
*   **Checkpoint 1**: 모호하고 충돌하는 요구사항의 파이프라인 유입 차단.
*   **Checkpoint 2**: 품질 미달 TC, 요구사항 근거 없는 TC의 자동화 단계 전달 차단.
*   **Checkpoint 3**: 신뢰할 수 없는 환경에서의 자동화 실행 결과 차단. (실행 전 Pre-check 및 실행 후 검증)
*   **Checkpoint 4**: 원본(Pytest) 결과와 최종 보고 수치(JSON) 간의 불일치 차단.

## 2. 상세 데이터 흐름 및 판정 순서

최종 판정은 반드시 다음 순서로 엄격하게 진행되어 순환 참조를 방지합니다.

1.  **Agent 4**가 테스트 결과, 로그, CP3 유효성을 종합하여 `표준 결과 초안(Draft)` 생성.
2.  **Checkpoint 4**가 `report.html`, `qa_results.json` 원본 데이터와 초안을 교차 검증.
3.  **VALIDATED** 판정 획득.
4.  전체 **Execution(실행 상태)** 계산.
5.  최종 **Release(릴리즈 권고)** 계산.
6.  **`agent4_summary.json`** 확정 저장 및 외부(Slack/Notion) 보고용 Payload 전송.

## 3. 4개 층의 상태값 분리

상태값은 서로 섞이지 않고 엄격한 층(Layer)을 유지합니다.

1.  **Pytest 원본 상태**: `Passed`, `Failed`, `Skipped`, `Error`
2.  **QA 원인 분류 (Agent 4)**: 
    *   `product_defect` (제품 결함 후보)
    *   `requirement_review` (요구사항 확인 필요)
    *   `environment_issue` (환경·시뮬레이터 문제)
    *   `automation_issue` (자동화 코드 문제)
    *   `not_executed` (조건 부족으로 미실행)
3.  **Checkpoint 4 상태**: `VALIDATED`, `BLOCKED`
4.  **최종 시스템 판정**:
    *   **Execution**: `PASSED`, `FAILED`, `INCOMPLETE`
    *   **Release**: `PASS`, `HOLD`

*(예시: 환경 문제로 인한 `Failed`는 Passed로 조작되지 않으며, CP4가 `VALIDATED`되더라도 Release는 `HOLD` 처리됩니다.)*

## 4. 최종 결과 파일 (SSOT)

*   **`agent4_summary.json`**: 최종 실행, 분류, 릴리즈 결과가 모두 담긴 유일한 기준 파일 (SSOT).
*   **`checkpoint4_validation.json`**: 원본 Report와 Agent 4 결과가 일치하는지 증명하는 단순 검증 감사 기록 (Audit Evidence).
