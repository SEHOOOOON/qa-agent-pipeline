# 🔗 QA 추적성 매트릭스 (Traceability Matrix)

본 매트릭스는 요구사항(Requirement)이 에이전트의 정제(Confirmed Fact)를 거쳐, 어떤 QA 기준(Criterion)과 테스트 케이스(TC)로 설계되고, 최종적으로 자동화 코드(Automation)를 통해 어떻게 검증(Result/Finding)되는지 보여주는 End-to-End 추적성 문서입니다.

이 구조적 추적성을 통해 **"테스트 누락 방지"**와 **"근거 없는 환각 Assert 차단"**을 완벽하게 통제합니다.

| Requirement ID | Confirmed Fact (Agent 1) | QA Criterion (Agent 2) | TC ID | Automation Script | Execution Result | Finding / Jira |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **REQ-001**<br/>(개별 제어) | **FACT-001**<br/>장치 1대 모드/온도/전원 제어 | **CRIT-CTRL-001**<br/>상태 전이 및 UI/Register 동기화 | **TC-01** | `test_tc01_single_device_mode_change` | 🟢 Pass | - |
| **REQ-002**<br/>(일괄 제어) | **FACT-002**<br/>다중 장치 동일 모드/온도 일괄 적용 | **CRIT-INT-002**<br/>다중 장비 일괄 제어 정합성 | **TC-INT-02** | `test_tc_int_02_multiple_devices_broadcast` | 🟢 Pass | - |
| **DOMAIN-RULE-002**<br/>(FAN 배타제어) | **FACT-003**<br/>FAN/DRY 모드 시 온도 조절 차단 | **CRIT-MODE-002**<br/>도메인 특화 배타 제어 | **TC-02A** | `test_tc02a_rule2_fan_mode_temp_disabled` | 🟢 Pass | - |
| **DOMAIN-RULE-003**<br/>(Lock 통제) | **FACT-004**<br/>전체 Lock 시 UI 제어 차단 | **CRIT-LOCK-001**<br/>권한 및 Lock 제어 통제 | **TC-04** | `test_tc04_lock_blocks_control` | 🟢 Pass | - |
| **REQ-005**<br/>(오류 UI 전이) | **FACT-005**<br/>CH05 통신 오류 시 에러 아이콘 점등 | **CRIT-ERR-001**<br/>오류 발생 시 UI/상태 동기화 | **TC-08** | `test_tc08_simulator_timeout_error` | 🔴 Fail | **[BUG-02]**<br/>통신 타임아웃 먹통 |
| **GAP-001**<br/>(에러 시 색상) | - (Information Gap으로 격리) | - (검증 제외 항목으로 명시) | **-** | - (자동화 스크립트 제외) | 🟡 Review | **REVIEW-001**<br/>기획 확인 필요 |
| **GAP-002**<br/>(타임아웃 문구) | - (Information Gap으로 격리) | - (검증 제외 항목으로 명시) | **-** | - (자동화 스크립트 제외) | 🟡 Review | **REVIEW-002**<br/>기획 확인 필요 |

---

### 💡 매트릭스 활용 효과
1. **환각 통제 증명**: `GAP-001`, `GAP-002`처럼 정보가 부족한 항목은 `Confirmed Fact`로 넘어오지 못하며, 자동화 스크립트에서도 철저히 배제됩니다.
2. **영향도 분석 (Impact Analysis)**: 특정 요구사항(Requirement)이 변경될 경우, 어떤 TC와 파이썬 스크립트 함수를 수정해야 하는지 1초 만에 파악할 수 있습니다.
3. **품질 가시성 확보**: 현재 제품에 남아있는 결함(BUG)과 기획 결함(REVIEW)이 어느 파트에서 발생했는지 정밀 추적이 가능합니다.
