# 🔗 요구사항·TC·자동화 추적성 매트릭스

본 매트릭스는 요구사항(Requirement)이 에이전트의 정제(Agent 1)를 거쳐, 어떤 테스트 케이스(Agent 2)로 설계되고, 최종적으로 자동화 코드(Agent 3)를 통해 어떻게 검증(Result/Finding)되는지 보여주는 추적성 문서입니다.

이 구조적 추적성을 통해 **"근거 없는 기대결과가 다음 단계로 전달될 위험을 줄이고"**, 요구사항이나 코드가 변경될 때 **"영향 범위를 빠르게 확인"**할 수 있습니다.

*안내: 본 매트릭스는 전체 TC 중 대표 TC만 수록한 샘플입니다. 전체 TC 목록은 `tests/test_controller.py`를 참조하세요.*

---

## A. 설계 추적성 매트릭스 (Design Traceability)
입력된 요구사항과 정보 부족(Gap)이 Agent 1, 2를 거쳐 테스트 케이스(TC)로 어떻게 변환되었는지, 그리고 각 Checkpoint를 통과했는지 추적합니다.
*(기능 전체 판정은 Agent 1 기준 일부 진행(Partial Proceed)이며, 아래 표의 Checkpoint 1 값은 개별 범위의 통과/제외 상태를 표시합니다.)*

| 항목 유형 | 근거 ID | 정제 결과 (Agent 1) | 품질 기준 (Agent 2) | TC ID | Checkpoint 1 | Checkpoint 2 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Requirement** | REQ-001 | **FACT-001** (개별 제어) | CRIT-CTRL-001 | **TC-MODE-001** | Passed Scope | Approved |
| **Requirement** | REQ-002 | **FACT-002** (일괄 제어) | CRIT-INT-001 | **TC-INT-002** | Passed Scope | Approved |
| **Domain Rule** | DOMAIN-RULE-002 | **FACT-003** (FAN 모드 온도 조절 차단) | CRIT-MODE-002 | **TC-MODE-002** | Passed Scope | Approved |
| **Domain Rule** | DOMAIN-RULE-002 | **FACT-003** (DRY 모드 온도 조절 차단 및 해제 검증) | CRIT-MODE-002 | **TC-MODE-003** | Passed Scope | Approved |
| **Domain Rule** | DOMAIN-RULE-003 | **FACT-004** (LOCK 시 중앙·현장 관제점 제어 차단) | CRIT-LOCK-001 | **TC-LOCK-001** | Passed Scope | Approved |
| **Requirement** | REQ-TEMP-001 | **FACT-005** (일반 모드 온도 경계 16~30°C) | CRIT-TEMP-001 | **TC-TEMP-001** | Passed Scope | Approved |
| **Requirement** | REQ-TEMP-002 | **FACT-007** (AUTO 모드 온도 경계 18~30°C) | CRIT-TEMP-002 | **TC-TEMP-002** | Passed Scope | Approved |
| **Requirement** | REQ-ERROR-001 | **FACT-006** (에러 제어 차단) | CRIT-ERR-001 | **TC-ERR-001** | Passed Scope | Approved |
| **Spec Gap** | REQ-ERROR-001 | **GAP-001** (에러 시 색상 정책) | Information Gap | - | Excluded | Not Applicable |
| **Spec Gap** | REQ-ERROR-002 | **GAP-002** (타임아웃 문구) | Information Gap | - | Excluded | Not Applicable |

---

## B. 실행 추적성 매트릭스 (Execution Traceability)
설계된 TC가 실제 자동화 함수(`tests/test_controller.py`)와 매핑되어 실행된 결과와 결함(Finding) 발생 현황을 추적합니다.

> **현재 상태**: 2026-07-26 통합 Run 실행 완료 (전체 13건 / Passed 8건 / Failed 3건 / Skipped 2건)

- **Source Test Run ID**: `3b6b4d33-ffca-4cdf-b8b4-3700b83cdb4f`
- **Agent 4 Analysis Run ID**: `RUN-20260726-184617`

| TC ID | 자동화 함수 (Automation Function) | Checkpoint 3 | 실행 상태 (Result) | 실행 증거 (Evidence) |
| :--- | :--- | :---: | :---: | :--- |
| **TC-MODE-001** | `test_tc_mode_001_heat_mode_and_temp_apply` | Pre-check Passed | **Passed** | Report Row + JSON Record |
| **TC-MODE-002** | `test_tc_mode_002_fan_mode_temp_disabled` | Pre-check Passed | **Passed** | Report Row + JSON Record |
| **TC-MODE-003** | `test_tc_mode_003_dry_mode_then_cool_reactivation` | Pre-check Passed | **Passed** | Report Row + JSON Record |
| **TC-LOCK-001** | `test_tc_lock_001_all_devices_full_inspection` | Pre-check Passed | **Passed** | Report Row + JSON Record |
| **TC-ERR-001** | `test_tc_err_001_ch05_fault_injection_control_block` | Pre-check Passed | **Passed** | Report Row + JSON Record |
| **TC-INT-002** | `test_tc_int_002_multi_select_batch_control` | Pre-check Passed | **Passed** | Report Row + JSON Record |
| **TC-TEMP-001** | `test_tc_temp_001_upper_limit_boundary` | Pre-check Passed | **Passed** | Report Row + JSON Record |

---

## C. QA 파이프라인 규칙 검증 (QA Pipeline Rule Validation)
이 표는 제품(Product)을 테스트하는 것이 아니라, Agent 1이 발견한 **정보 부족(Gap) 항목이 제품 기능 TC의 통과·실패 기준에서 정상적으로 제외(Isolation)되는지**, 그리고 의도적인 비통과 시나리오가 파이프라인을 통해 올바르게 원인 분류되는지 확인하는 파이프라인 규칙 검증입니다.

> 💡 **GAP-002와 TC-PIPE-002의 목적 차이 안내**
> GAP-002(정보 부족)로 인해 통신 Timeout 발생 시 나타나야 할 정확한 Toast 문구 Assert는 제품 기능 TC에서 제외됩니다.
> 단, Timeout 자체를 강제 발생시켰을 때 이 오류가 시스템에 의해 `environment_issue`로 정확히 원인 분류되고 원본 Failed 상태를 유지하는지 확인하는 작업은 Pipeline Validation(TC-PIPE-002)으로 별도 수행합니다.

| 분류 목적 | 자동화 함수 (Pipeline Validation Function) | 실행 상태 | 분류 결과 (Finding ID) |
| :--- | :--- | :---: | :---: |
| 요구사항 확인 필요 검증 | `test_pipeline_001_alarm_ui_ambiguity_classification` (TC-PIPE-001) | **Skipped** | `requirement_review` |
| 환경·시뮬레이터 문제 검증 | `test_pipeline_002_simulator_timeout_classification` (TC-PIPE-002) | **Failed** | `environment_issue` (ENV-001) |
| 자동화 코드 문제 검증 | `test_pipeline_003_automation_code_error_classification` (TC-PIPE-003) | **Failed** | `automation_issue` (AUT-001) |
| 조건 부족으로 미실행 검증 | `test_pipeline_004_not_executed_condition_missing` (TC-PIPE-004) | **Skipped** | `not_executed` (SKIP-001) |
| 제품 결함 후보 검증 | `test_tc_temp_002_auto_mode_lower_limit` (TC-TEMP-002) | **Failed** | `product_defect` (DEF-001) |

---

## D. Checkpoint 4 최종 릴리즈 요약
기능 검증은 모두 통과(Passed)하였으나, 파이프라인 정합성 검증을 위한 의도적 비통과 시나리오(Failed/Skipped)가 포함된 통합 Run이므로, Checkpoint 4가 이를 올바르게 탐지하여 릴리즈를 차단(HOLD)하는지 확인합니다.

- **Checkpoint 4 Status**: `VALIDATED` (데이터 정합성 통과)
- **JSON Total**: 13
- **HTML Total**: 13
- **Consistency Errors**: 0
- **Execution**: `FAILED` (비통과 TC 감지)
- **최종 Release**: `HOLD` (릴리즈 차단 성공)

---

### 💡 매트릭스 분리 및 구조화 효과
1. **역할별 가시성 확보**: 설계(기획 ↔ TC)와 실행(TC ↔ 코드), 그리고 파이프라인 규칙 검증을 분리하여 각 부서(기획/QA/개발)가 필요한 정보를 독립적으로 확인할 수 있습니다.
2. **환각 및 결손 통제 증명**: `GAP`으로 분류된 항목은 제품 기능 테스트에 포함되지 않고 **`QA 파이프라인 규칙 검증`** 으로 분리되어 통제됨을 확실하게 보여줍니다. (근거 없는 기대결과가 통과/실패 기준에 오염되는 것을 방지)
3. **결함의 엄격한 분류**: 실행 후 실제 결과에 따라, 제품 결함(Product Defect)과 환경 이슈(Environment Issue)를 구분하여 정확하게 격리 및 보고합니다.
