# 🤖 Agent 2: 테스트 케이스 명세서 (Test Case Document)

## 파트 1: [기능별 QA 기준 및 추적성 정의]
1. **기준명**: 개별 장비 및 다중 장비 상태 제어
2. **적용 대상**: Virtual Central Controller UI 및 하부 장비 제어 로직
3. **품질 목적**: 사용자가 조작한 모드/온도/전원 값이 정확히 대상 장비에만 적용되고, 도메인 제약(FAN 모드 시 온도 잠금 등)이 준수되는지 확인한다.
4. **기대 동작**: 대상 장비의 UI 상태와 내부 Register 값이 정확히 동기화된다.
5. **검증 제외 항목**: 에러 시 카드 UI 색상 규칙, 통신 타임아웃 안내 문구 (Agent 1 정보 부족 사유)
6. **Pass/Fail 기준**: 
   - [Pass] 요구사항(Confirmed Facts)에 명시된 모든 제어/상태 변경이 대상 장비에만 정확히 반영됨.
   - [Fail] 비대상 장비의 상태가 오염되거나, 명시되지 않은 값으로 UI/Register가 변경됨.

---

## 파트 2: [Test Case 목록 및 상세 명세]

### [그룹 A: Atomic TCs (개별 관제점 독립 검증)]

#### 1. TC_ID 및 제목: TC-01_단일장비_모드변경_정합성
2. **요구사항 추적성**:
   - Requirement ID: REQ-001
   - Source Evidence: 실내기 한 대 개별 제어 가능
   - Applied QA Criteria: 상태 전이, UI/Register 동기화 (Tier 1)
   - Risk Covered: 모드 변경 시 UI에만 적용되고 Register에 반영되지 않는 문제 방지
3. **테스트 독립성**:
   - Test Data / Initial State: 장치 1 (online=true, locked=false, mode=COOL, setTemp=24)
   - Setup Method: `load_clean_simulator(page)` 호출 후 장치 1 선택
   - Cleanup / Restore: 페이지 새로고침을 통해 초기 상태 복원
   - Independence Check: 단독 실행 가능 (Yes)
4. **Steps (Action)**:
   - 장치 1 선택
   - 제어 패널에서 [HEAT] 모드 버튼 클릭
   - [Apply] 버튼 클릭
5. **Expected Results (Assert)**: 
   - **UI Assert**: 장치 1의 모드 아이콘이 'HEAT'로 변경됨.
   - **Register Assert**: `devices[1].mode == "HEAT"`로 변경됨.
   - *Double-Assert 필수 적용 대상 (UI+상태 전이)*
6. **검증 제외 (Excluded Assertions)**: 에러 색상, 에러 문구

#### 2. TC_ID 및 제목: TC-02A_Rule2_송풍모드_온도조절_비활성화
2. **요구사항 추적성**:
   - Requirement ID: DOMAIN-RULE-002
   - Source Evidence: FAN/DRY 모드 시 온도 조절 차단
   - Applied QA Criteria: 도메인 특화 배타 제어 (Tier 2)
   - Risk Covered: FAN 모드에서 온도가 변경되어 하드웨어 에러를 유발할 위험
3. **테스트 독립성**:
   - Test Data / Initial State: 장치 1 (online=true, mode=COOL)
   - Setup Method: 장치 1 선택 후 FAN 모드 적용
   - Cleanup / Restore: 페이지 새로고침
   - Independence Check: 단독 실행 가능 (Yes)
4. **Steps (Action)**:
   - 제어 패널에서 [FAN] 모드 버튼 클릭
   - 온도 조절 영역 상태 확인
5. **Expected Results (Assert)**: 
   - **UI Assert**: 온도 조절 영역(Up/Down 버튼 등)이 `disabled` 처리됨.
   - **Register Assert**: (UI-only Allowed: 상태 입력 차단 여부 확인이므로 Register 갱신 불필요)
6. **검증 제외 (Excluded Assertions)**: 없음

---

### [그룹 B: Integration TCs (전체 관제점 일괄 적용 E2E 정합성 검증)]

#### 1. TC_ID 및 제목: TC-INT-02_복수장비_일괄제어_정합성
- **Expected Results (Assert)**:
  - **대상 장비 Assert**: 선택한 장치 1, 2, 3의 `mode`가 모두 `"HEAT"`로 변경되고 UI 동기화 완료.
  - **비대상 장비 불변 Assert**: 선택하지 않은 장치 4~16의 `mode` 및 `setTemp`는 기존 값을 100% 유지함.

---

## 📄 [Data Contract] Agent 2 Output
```yaml
tc_id: "TC-01_단일장비_모드변경_정합성"
requirement_ids: ["REQ-001"]
qa_criteria: ["상태 전이", "UI/Register 동기화"]
preconditions: "장비가 온라인 상태이며 제어권이 있음"
setup: "초기 페이지 로드 및 장치 1 단일 선택"
steps: 
  - "HEAT 버튼 클릭"
  - "Apply 클릭"
expected_ui: ["장치 1 모드 아이콘 HEAT"]
expected_register: ["devices[1].mode == 'HEAT'"]
negative_assertions: []
cleanup: "시뮬레이터 상태 초기화"
automation_level: "Automated"
review_status: "Draft"
```
