# 🟢 Agent 2: 테스트케이스 수정본 (Checkpoint 2 피드백 반영)
*안내: Checkpoint 2의 수정 요청을 반영한 재검토 대상 산출물입니다. 최종 승인 여부는 Checkpoint 2 재검토 결과에서 결정합니다.*

```yaml
test_cases:
  - tc_id: "TC-MODE-001"
    title: "단일장비 모드변경 정합성 (COOL -> HEAT)"
    requirement_ids: ["REQ-001"]
    source_evidence: ["실내기 한 대 개별 제어 가능"]
    qa_criteria: ["공통: 상태 전이 검증", "도메인: UI 및 내부 상태 정합성"]
    quality_standard_ids: ["CRIT-CTRL-001"]
    risk_covered: ["모드 변경 시 UI에만 적용되고 Register에 반영되지 않는 문제 방지"]
    initial_state: 
      online: true
      locked: false
      mode: "COOL"
      setTemp: 24
    preconditions: 
      - "장비가 온라인 상태이며 제어권이 있음"
    setup: 
      - "load_clean_simulator(page) 호출로 초기화"
      - "장치 1 선택"
    steps: 
      - "제어 패널에서 [HEAT] 모드 버튼 클릭"
      - "[Apply] 버튼 클릭"
    expected_ui: 
      - "모드 배지 텍스트가 '난방'으로 변경됨."
    expected_device_state: 
      - "devices.find(d => d.id === 1).mode === 'HEAT'"
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "resetSimulatorState() 호출 (또는 기기 설정 전체 초기화 클릭)"
    double_assert_policy: "Required"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Revised"

  - tc_id: "TC-MODE-002"
    title: "Rule2 송풍모드 전환 UI/Register 동기화"
    requirement_ids: ["DOMAIN-RULE-002"]
    source_evidence: ["FAN 모드 지원"]
    qa_criteria: ["공통: 상태 전이 검증"]
    quality_standard_ids: ["CRIT-MODE-002"]
    risk_covered: ["모드 변경 UI/Register 불일치"]
    initial_state: 
      online: true
      locked: false
      mode: "COOL"
    preconditions: []
    setup: 
      - "load_clean_simulator(page) 호출 후 장치 1 선택"
    steps: 
      - "제어 패널에서 [FAN] 모드 버튼 클릭"
      - "[Apply] 버튼 클릭"
    expected_ui: 
      - "모드 배지 텍스트가 '송풍'으로 변경됨."
    expected_device_state: 
      - "devices.find(d => d.id === 1).mode === 'FAN'"
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "resetSimulatorState() 호출"
    double_assert_policy: "Required"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Revised"

  - tc_id: "TC-MODE-003"
    title: "Rule2 송풍모드 시 온도조절 UI 비활성화"
    requirement_ids: ["DOMAIN-RULE-002"]
    source_evidence: ["FAN/DRY 모드 시 온도 조절 차단"]
    qa_criteria: ["기능별: 모드별 제어 제한 (배타 제어)"]
    quality_standard_ids: ["CRIT-MODE-002"]
    risk_covered: ["FAN 모드에서 허용되지 않은 온도 제어가 전달되어 UI와 내부 제어 상태가 불일치할 위험 방지"]
    initial_state: 
      online: true
      locked: false
      mode: "FAN"
    preconditions: 
      - "기기가 이미 FAN 모드로 설정되어 있음"
    setup: 
      - "load_clean_simulator() 호출 (초기화)"
      - "장치 1 선택"
      - "FAN 모드 클릭 및 적용"
    steps: 
      - "온도 조절 영역 상태(Up/Down 버튼 등) 확인"
    expected_ui: 
      - "온도 UP 버튼 disabled === true"
      - "온도 DOWN 버튼 disabled === true"
    expected_device_state: []
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "resetSimulatorState() 호출"
    double_assert_policy: "UI-only"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Revised"

  - tc_id: "TC-INT-02"
    title: "복수 장비 일괄 제어 정합성"
    requirement_ids: ["REQ-002"]
    source_evidence: ["다중 선택 후 일괄 명령 전송 가능"]
    qa_criteria: ["기능별: 모드별 제어 제한 (배타 제어)", "도메인: 다중 장비 제어 일치성"]
    quality_standard_ids: ["CRIT-INT-001"]
    risk_covered: ["일괄 제어 시 비대상 기기까지 상태가 변경되는 치명적 오염 오류 방지"]
    initial_state: 
      devices: "모두 COOL 모드, 24도"
    preconditions: 
      - "복수 제어 모드가 활성화되어 있음"
    setup: 
      - "load_clean_simulator(page) 호출"
      - "기존 devices 배열의 상태를 Snapshot으로 저장 (before_devices)"
    steps: 
      - "장치 1, 2, 3 선택"
      - "제어 패널에서 [HEAT] 모드 버튼 클릭"
      - "[Apply] 버튼 클릭"
    expected_ui: 
      - "장치 1, 2, 3의 모드 배지가 '난방'으로 변경됨"
    expected_device_state: 
      - "devices.find(d => d.id === 1).mode === 'HEAT'"
      - "devices.find(d => d.id === 2).mode === 'HEAT'"
      - "devices.find(d => d.id === 3).mode === 'HEAT'"
    negative_assertions: []
    unchanged_state_assertions: 
      - "비대상 장비(4~16)의 mode 값이 실행 전 Snapshot과 동일함 (before_devices[i].mode === after_devices[i].mode)"
      - "비대상 장비(4~16)의 setTemp 값이 실행 전 Snapshot과 동일함"
      - "대상 장비(1~3)의 locked, online 등 제어 비대상 필드도 실행 전과 동일함"
    excluded_assertions: []
    cleanup: 
      - "복수 제어 모드 해제 및 resetSimulatorState() 호출"
    double_assert_policy: "Required"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Revised"
```
