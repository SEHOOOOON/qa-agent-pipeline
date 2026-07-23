# QA Pipeline Architecture

본 문서는 파이프라인의 핵심 설계와 Agent/Checkpoint의 역할, 데이터 흐름, 상태값 판정 기준 및 전체 프로세스를 정의하는 **Single Source of Truth (SSOT)** 구현 기준 문서입니다. 외부 설명용 프로세스와 내부 구현 기준을 함께 제공합니다.

## 1. 프로젝트 목적

본 파이프라인은 복잡한 중앙제어 시스템 도메인에서 발생하는 요구사항 모호성, TC 품질 저하, 테스트 환경 문제, 스크립트 결함 등을 조기에 차단하고 검증하기 위해 구축되었습니다.
단순 UI 자동화가 아닌, 도메인 지식(3-Tier QA 기준)과 상태 전이 로직을 반영한 **신뢰할 수 있는 QA 자동화 생태계**를 목표로 합니다.

## 2. 전체 프로세스

파이프라인의 근본 원칙은 다음과 같습니다.
> **"Agent는 만든다. Checkpoint는 검사하고 막는다."**

*   **Agent (실행 주체)**: 새로운 산출물이나 결과를 생성합니다.
*   **Checkpoint (품질 게이트)**: Agent가 생성한 산출물을 검증하여 다음 단계로 전달해도 되는지 평가합니다. 절대 새로운 데이터를 창조하지 않습니다.

## 3. 개발 전 QA와 개발 후 QA

신규 기능이나 변경 요구사항이 접수됐을 때 파이프라인이 1단계부터 4단계까지 단번에 직렬로 실행되는 것은 아닙니다. 구현 단계를 중심으로 **개발 전 QA**와 **개발 후 QA**로 명확히 나뉩니다.

### 3-1. 개발 전 QA (Agent 1 ➔ CP1 ➔ Agent 2 ➔ CP2)
*   **목적**: "무엇을 만들어야 하는가?", "어떤 정보가 부족한가?", "어떤 테스트가 필요한가?"를 사전에 정의합니다.
*   이 단계에서는 실제 UI나 코드가 없어도 요구사항(기획서, Jira 등)만으로 동작합니다.
*   **산출물**: 확정 정보, 정보 부족(Gap), 테스트 가능 범위, 3-Tier 기준이 적용된 '승인된 테스트케이스(TC)'.

### 3-2. 개발 및 자동화 준비 (Human)
*   CP2가 승인되었다고 Agent 3가 바로 실행되지 않습니다.
*   **개발팀**: UI, API, 상태 로직 등을 구현합니다.
*   **QA 자동화 엔지니어**: 승인된 TC에 대응하는 Playwright 함수(Pytest)를 작성하고, `TC ID`와 자동화 함수를 매핑(Mapping)합니다.

### 3-3. 개발 후 QA (CP3 Pre-check ➔ Agent 3 ➔ CP3 Post-check ➔ Agent 4 ➔ CP4)
*   **목적**: "승인된 TC를 실행할 수 있는가?", "결과를 신뢰할 수 있는가?", "릴리즈 가능한 상태인가?"를 판정합니다.
*   이 단계에서 실제 Playwright 테스트가 구동되며, 최종 결함 원인 분류와 릴리즈 권고가 도출됩니다.

## 4. Agent와 Checkpoint 책임

### Agent별 책임
*   **Agent 1**: 정제된 요구사항 생성, 영향 관제점 분석, 테스트 가능 범위 확정. (UI, TC 생성 및 Pass/Fail 판정 **금지**)
*   **Agent 2**: 3-Tier QA 기준(공통/도메인/기능)을 적용하여 테스트케이스(TC) 생성.
*   **Agent 3**: 승인된 TC와 매핑된 Playwright 자동화 테스트 실행 및 증거(로그, 상태) 기록. (TC를 코드로 변환하는 로직 **없음**)
*   **Agent 4**: 5가지 QA 원인 분류 수행, 최종 실행 결과 및 릴리즈 판정 계산.

### Checkpoint별 책임
*   **Checkpoint 1**: 모호하고 충돌하는 요구사항의 파이프라인 유입 차단.
*   **Checkpoint 2**: 품질 미달 TC, 요구사항 근거 없는 TC의 자동화 단계 전달 차단.
*   **Checkpoint 3**: 신뢰할 수 없는 환경에서의 자동화 실행 결과 차단. (`TC-ENV-000`을 통한 실행 전 Pre-check 및 실행 후 상태 검증)
*   **Checkpoint 4**: pytest-html과 커스텀 JSON Collector로 저장된 두 결과 수집 경로를 비교해 TC 누락·중복, 상태 변형과 집계 불일치를 차단합니다.

## 5. 실제 실행 및 데이터 흐름

최종 판정은 반드시 다음 순서로 엄격하게 진행되어 순환 참조를 방지합니다.

1.  **Agent 4**가 `qa_results.json`과 `report.html` 로드.
2.  **Agent 4 내부 Checkpoint 4**가 ID·상태·건수·집계 정합성 교차 검증.
3.  **`checkpoint4_validation.json`** 저장 (VALIDATED 판정 획득 여부 기록).
4.  검증 결과를 포함해 전체 **Execution(실행 상태)** 계산.
5.  최종 **Release(릴리즈 권고)** 계산.
6.  **`agent4_summary.json`** 저장 확정.
7.  VALIDATED인 경우 **Slack·Notion 전송** (외부 보고용 Payload).

## 6. 상태값과 릴리즈 판정

상태값은 서로 섞이지 않고 엄격한 4개의 층(Layer)을 유지합니다.

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

## 7. 통합 Run과 의도적 비통과

포트폴리오 시연 환경(V1)에서는 파이프라인 전체의 톱니바퀴 동작을 검증하기 위해 정상 기능 검증과 **의도적 비통과 시나리오**를 하나의 통합 Run으로 함께 실행합니다.

*   정상 기능 TC
*   요구사항 모호성 시나리오 (주입)
*   환경 문제 시나리오 (주입)
*   자동화 문제 시나리오 (주입)
*   제품 결함 후보 시나리오 (주입)

> **💡 핵심 원칙**: 포트폴리오 V1에서는 `TC-PIPE-*` 및 분류 검증용 TC를 통해 의도적 비통과 시나리오를 구분합니다. `scenario_type` 메타데이터를 통한 자동 구분은 고도화 대상입니다.

## 8. 대표 시나리오

**배경**: 기존 중앙제어 시스템에 "FAN/DRY 모드의 설정온도 조작 제한"과 "COOL/HEAT 복귀 시 재활성화 정책"이 변경 요구사항으로 접수된 상황.

1.  **Agent 1**: 확정 정보(FAN/DRY 온도 조작 차단) 추출. 정보 부족(온도 표시 방식) 추출.
2.  **Checkpoint 1**: 명확한 범위(PARTIAL_PROCEED)만 승인하여 다음 단계로 전달.
3.  **Agent 2**: 3-Tier(상태 전이, 비대상 장비 동기화 등)를 적용하여 온도 제한 TC 설계.
4.  **Checkpoint 2**: TC 독립성 및 기대결과 명확성 검증 후 승인.
5.  **개발/준비**: `TC-MODE-002` 등과 Playwright 함수 매핑 완료.
6.  **Agent 3**: `TC-ENV-000`(Pre-check) 실행 후 Playwright 자동화 구동.
7.  **Agent 4 / Checkpoint 4**: 결과 분류 및 원본 정합성 검증 완료 ➔ 최종 **릴리즈 판정**.

## 9. 최종 산출물과 SSOT

데이터의 역할은 철저히 나뉩니다.

*   **`qa_results.json`**: Pytest 실행 결과의 커스텀 원본 데이터.
*   **`report.html`**: 사람 확인 및 독립 수집 경로 대조용 실행 리포트.
*   **`checkpoint4_validation.json`**: Report·JSON 정합성 검증 감사 기록 (Audit Evidence).
*   **`agent4_summary.json`**: 검증된 결과, 원인 집계, Execution과 Release를 포함한 최종 SSOT.

## 10. 현재 한계 (V2 고도화 대상)

*   JSON 레벨의 `scenario_type` 메타데이터 부재 (현재는 TC Prefix로 구분).
*   Setup/Teardown 단계의 에러가 JSON Collector(call 단계)에 누락될 위험 존재. (단, 현재도 CP4에서 정합성 오류로 걸러져 차단되는 Fail-Closed로 방어됨).
