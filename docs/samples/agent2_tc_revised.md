# 🟢 Agent 2: 테스트케이스 수정본 (Checkpoint 2 승인 완료)
*안내: Checkpoint 2의 수정 요청을 반영하여 재검토한 산출물입니다. Checkpoint 2 재검토(Review After)에서 모든 TC가 **Approved** 판정을 받았습니다.*
*본 문서는 전체 자동화 TC 중 품질 검토 과정을 보여주는 **대표 TC**만 수록합니다. 전체 TC 목록은 `tests/test_controller.py`를 참조하세요.*

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
      setTemp: 24.0
    preconditions: 
      - "장비가 온라인 상태이며 제어권이 있음"
    setup: 
      - "load_clean_simulator(page) 호출로 초기화"
      - "장치 1 선택"
    steps: 
      - "제어 패널에서 [HEAT] 모드 버튼 클릭"
      - "설정온도를 26.0°C로 변경"
      - "[Apply] 버튼 클릭"
    expected_ui: 
      - "모드 배지 텍스트가 '난방'으로 변경됨."
      - "설정온도 표시값이 '26.0°C'임"
    expected_device_state: 
      - "devices.find(d => d.id === 1).mode === 'HEAT'"
      - "devices.find(d => d.id === 1).setTemp === 26.0"
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "resetSimulatorState() 호출 (또는 기기 설정 전체 초기화 클릭)"
    double_assert_policy: "Required"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Approved"

  - tc_id: "TC-MODE-002"
    tc_category: "엣지케이스"
    title: "FAN 모드 선택 시 설정온도 조절 UI 비활성화"
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
    expected_ui: 
      - "온도 UP 버튼 disabled === true"
      - "온도 DOWN 버튼 disabled === true"
      - "설정온도 표시값이 '---'임"
    expected_device_state: []
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "resetSimulatorState() 호출"
    double_assert_policy: "UI-only"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Approved"

  - tc_id: "TC-MODE-003"
    tc_category: "엣지케이스"
    title: "Rule 2 양방향 | 제습(DRY) 비활성화 → 냉방(COOL) 복귀 시 설정온도 관제점 재활성화"
    requirement_ids: ["DOMAIN-RULE-002"]
    source_evidence: ["FAN/DRY 모드 시 온도 조절 차단"]
    qa_criteria: ["기능별: 모드별 제어 제한 (배타 제어)"]
    quality_standard_ids: ["CRIT-MODE-002"]
    risk_covered: ["모드 복귀 시 UI 활성화 상태가 갱신되지 않는 문제 방지"]
    initial_state: 
      online: true
      locked: false
      mode: "COOL"
    preconditions: []
    setup: 
      - "load_clean_simulator() 호출"
      - "장치 1 선택"
    steps: 
      - "제어 패널에서 [DRY] 모드 버튼 클릭"
      - "온도 조절 UI 비활성화 확인"
      - "제어 패널에서 [COOL] 모드 버튼 클릭"
    expected_ui: 
      - "DRY 모드에서 UP·DOWN 버튼 disabled === true"
      - "COOL 복귀 후 UP·DOWN 버튼 disabled === false"
      - "COOL 복귀 후 설정온도에 '°C'가 표시됨"
    expected_device_state: []
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "resetSimulatorState() 호출"
    double_assert_policy: "UI-only"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Approved"

  - tc_id: "TC-INT-002"
    tc_category: "엣지케이스"
    title: "복수 선택 일괄 제어 | 3대 선택 → HEAT 일괄 적용 → 내부 상태(devices[].mode) 검증"
    requirement_ids: ["REQ-002"]
    source_evidence: ["다중 선택 후 일괄 명령 전송 가능"]
    qa_criteria: ["기능별: 모드별 제어 제한 (배타 제어)", "도메인: 다중 장비 제어 일치성"]
    quality_standard_ids: ["CRIT-INT-001"]
    risk_covered: ["일괄 제어 시 비대상 기기까지 상태가 변경되는 치명적 오염 오류 방지"]
    initial_state: 
      devices: "모두 COOL 모드, 24.0°C"
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
    unchanged_state_assertions: []
    excluded_assertions: 
      - "V1 자동화 코드에서는 미구현. 비대상 장비(4~16)의 실행 전·후 Snapshot 비교는 V2 자동화 고도화 범위"
    cleanup: 
      - "복수 제어 모드 해제 및 resetSimulatorState() 호출"
    double_assert_policy: "Required"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Approved"
```
