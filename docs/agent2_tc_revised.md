# 🤖 Agent 2: 테스트 케이스 최종본 (Revised)
*안내: Checkpoint 2의 피드백을 수용하여 환각(Hallucination) 및 논리적 오류를 모두 수정한 최종 TC 산출물 샘플입니다.*

```yaml
test_cases:
  - tc_id: "TC-MODE-001"
    title: "단일장비 모드변경 정합성 (COOL -> HEAT)"
    requirement_ids: ["REQ-001"]
    source_evidence: ["실내기 한 대 개별 제어 가능"]
    qa_criteria: ["상태 전이", "UI/Register 동기화"]
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
    expected_register: 
      - "devices.find(d => d.id === 1).mode === 'HEAT'"
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: 
      - "에러 색상, 에러 문구 (Agent 1 기획 확인 필요 항목)"
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
    qa_criteria: ["상태 전이"]
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
    expected_register: 
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
    qa_criteria: ["도메인 특화 배타 제어"]
    risk_covered: ["FAN 모드에서 허용되지 않은 온도 제어가 전달되어 UI와 내부 제어 상태가 불일치할 위험 방지"]
    initial_state: 
      online: true
      locked: false
      mode: "FAN"
    preconditions: 
      - "기기가 이미 FAN 모드로 설정되어 있음"
    setup: 
      - "TC-MODE-002 수행 완료 상태 또는 시뮬레이터에서 FAN 강제 주입 후 장치 1 선택"
    steps: 
      - "온도 조절 영역 상태(Up/Down 버튼 등) 확인"
    expected_ui: 
      - "온도 UP 버튼 disabled === true"
      - "온도 DOWN 버튼 disabled === true"
    expected_register: []
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
    requirement_ids: ["REQ-005"]
    source_evidence: ["다중 선택 후 일괄 명령 전송 가능"]
    qa_criteria: ["상태 오염 방지", "배치 제어 정합성"]
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
    expected_register: 
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
