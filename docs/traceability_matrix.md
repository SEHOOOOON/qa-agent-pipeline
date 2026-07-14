# 🔗 QA 추적성 매트릭스 (Traceability Matrix)

본 매트릭스는 요구사항(Requirement)이 에이전트의 정제(Agent 1)를 거쳐, 어떤 테스트 케이스(Agent 2)로 설계되고, 최종적으로 자동화 코드(Agent 3)를 통해 어떻게 검증(Result/Finding)되는지 보여주는 End-to-End 추적성 문서입니다.

이 구조적 추적성을 통해 **"근거 없는 Assert가 다음 단계로 전달될 가능성을 차단"**하고, 요구사항이나 코드가 변경될 때 **"영향 범위를 빠르게 확인"**할 수 있습니다.

---

## A. 설계 추적성 매트릭스 (Design Traceability)
입력된 요구사항과 정보 부족(Gap)이 Agent 1, 2를 거쳐 테스트 케이스(TC)로 어떻게 변환되었는지, 그리고 각 Checkpoint를 통과했는지 추적합니다.

| Item Type | Source ID | Agent 1 (Fact/Gap) | QA Criterion (Agent 2) | TC ID | Checkpoint 1 | Checkpoint 2 |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **Requirement** | REQ-001 | **FACT-001** (개별 제어) | CRIT-CTRL-001 | **TC-MODE-001** | Proceed | Approved |
| **Requirement** | REQ-002 | **FACT-002** (일괄 제어) | CRIT-INT-001 | **TC-INT-001** | Proceed | Approved |
| **Domain Rule** | DOMAIN-RULE-002 | **FACT-003** (FAN 배타 제어) | CRIT-MODE-002 | **TC-MODE-002** | Proceed | Approved |
| **Domain Rule** | DOMAIN-RULE-003 | **FACT-004** (전체 Lock 통제) | CRIT-LOCK-001 | **TC-LOCK-001** | Proceed | Approved |
| **Spec Gap** | REQ-ERROR-001 | **GAP-001** (에러 시 색상 정책) | Information Gap | - | Excluded | Not Applicable |
| **Spec Gap** | REQ-ERROR-002 | **GAP-002** (타임아웃 문구) | Information Gap | - | Excluded | Not Applicable |
| **Spec Gap** | REQ-001 | **GAP-003** (온도 상하한계 누락) | Information Gap | - | Excluded | Not Applicable |

---

## B. 실행 추적성 매트릭스 (Execution Traceability)
설계된 TC가 실제 자동화 함수(`test_controller.py`)와 매핑되어 실행된 결과와 결함(Finding) 발생 현황을 추적합니다.

> ⚠️ **현재 상태**: 실행 대기 (Pending) - 자동화 스크립트는 준비되었으나 파이프라인에서 정식 실행 및 리포트 생성을 하기 전 상태입니다.

| TC / Gap ID | Automation Function | Run ID | Checkpoint 3 | Execution Status | Result | Finding ID | Checkpoint 4 | Evidence |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| **TC-MODE-001** | `test_tc01_happy_path_heat_mode_and_temp_apply` | - | Pending | **NOT_RUN** | - | - | Pending | - |
| **TC-INT-001** | `test_tc05_multi_select_batch_control` | - | Pending | **NOT_RUN** | - | - | Pending | - |
| **TC-MODE-002** | `test_tc02a_rule2_fan_mode_temp_disabled` | - | Pending | **NOT_RUN** | - | - | Pending | - |
| **TC-LOCK-001** | `test_tc03_lock_all_devices_full_inspection` | - | Pending | **NOT_RUN** | - | - | Pending | - |
| **GAP-001** | `test_tc07_alarm_ui_ambiguity_classification` | - | Pending | **NOT_RUN** | - | **REVIEW-001** | Pending | - |
| **GAP-002** | `test_tc08_hardware_timeout_exclusion` | - | Pending | **NOT_RUN** | - | **ENV-001** | Pending | - |

---

### 💡 매트릭스 분리 및 구조화 효과
1. **역할별 가시성 확보**: 설계(기획 ↔ TC)와 실행(TC ↔ 코드)을 분리하여 각 부서(기획/QA/개발)가 필요한 정보를 독립적으로 확인할 수 있습니다.
2. **환각 및 결손 통제 증명**: `GAP`으로 분류된 항목은 설계 단계에서 `Excluded` 처리되어 불필요한 자동화 코드로 넘어오지 않음을 확실하게 보여줍니다. (불필요한 리소스 낭비 방지)
3. **결함(Finding)의 엄격한 분류**: 실행 실패가 반드시 제품의 결함(Product Defect)을 의미하지 않습니다. TC-08의 경우 가상 환경 문제이므로 `BUG`가 아닌 `ENV-001` (환경 이슈)로 정확하게 격리하여 보고합니다.
