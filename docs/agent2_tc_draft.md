# 🤖 Agent 2: 초기 테스트 케이스 초안 (Draft)
*주의: 본 문서는 AI의 환각(Hallucination) 및 규칙 위반을 의도적으로 포함한 Agent 2의 최초 생성물 초안(Draft) 샘플입니다. Checkpoint 2에서 반려(Needs Revision)될 예정입니다.*

```yaml
test_cases:
  - tc_id: "TC-01"
    title: "단일장비 모드변경 정합성"
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
      - "load_clean_simulator(page) 호출 후 장치 1 선택"
    steps: 
      - "제어 패널에서 [HEAT] 모드 버튼 클릭"
      - "[Apply] 버튼 클릭"
    expected_ui: 
      - "모드 아이콘이 'HEAT'로 변경됨." # ❌ 결함: 실제 화면 문구 "난방"과 불일치 가능성
    expected_register: 
      - "devices[1].mode == 'HEAT'" # ❌ 결함: 인덱스(1)와 ID(1) 매핑 모호성
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: 
      - "에러 색상, 에러 문구"
    cleanup: 
      - "페이지 새로고침" # ❌ 결함: 상태 초기화(resetSimulatorState)를 명시하지 않음
    double_assert_policy: "Required"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Draft"

  - tc_id: "TC-02A"
    title: "Rule2 송풍모드 온도조절 비활성화"
    requirement_ids: ["DOMAIN-RULE-002"]
    source_evidence: ["FAN/DRY 모드 시 온도 조절 차단"]
    qa_criteria: ["도메인 특화 배타 제어"]
    risk_covered: ["FAN 모드에서 온도가 변경되어 하드웨어 에러를 유발할 위험"] # ❌ 결함: 하드웨어 에러 유발이라는 근거 없는 추측
    initial_state: 
      online: true
      mode: "COOL"
    preconditions: []
    setup: 
      - "장치 1 선택 후 FAN 모드 적용" # ❌ 결함: Setup과 Step의 동작 중복
    steps: 
      - "제어 패널에서 [FAN] 모드 버튼 클릭"
      - "온도 조절 영역 상태 확인"
    expected_ui: 
      - "온도 조절 영역(Up/Down 버튼 등)이 disabled 처리됨"
    expected_register: 
      - "(UI-only Allowed: 상태 입력 차단 여부 확인이므로 Register 갱신 불필요)" # ❌ 결함: Assert 칸에 미적용 사유를 적음
    negative_assertions: []
    unchanged_state_assertions: []
    excluded_assertions: []
    cleanup: 
      - "페이지 새로고침"
    double_assert_policy: "UI-only"
    automation_level: "Automated"
    independent_execution: true
    review_status: "Draft"

  - tc_id: "TC-INT-02"
    title: "복수 장비 일괄 제어 정합성"
    # ❌ 결함: requirement_ids, initial_state, setup 등 필수 항목 누락
    expected_ui: 
      - "장치 1, 2, 3의 모드가 'HEAT'로 변경됨"
    expected_register: 
      - "장치 1, 2, 3의 mode == 'HEAT'"
    unchanged_state_assertions: 
      - "선택하지 않은 장치들은 기존 값을 100% 유지함" # ❌ 결함: '100% 유지'라는 모호한 금지어 사용
    review_status: "Draft"
```
