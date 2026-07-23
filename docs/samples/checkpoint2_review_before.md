---
document_version: "1.0"
source_document: "agent2_tc_draft.md"
source_version: "1.0"
reviewed_at: "2026-07-23"
review_status: "Needs Revision"
---

# 🛑 Checkpoint 2: TC 품질 리뷰 리포트 (Review Before)

## 1. TC 총평
- **최종 판정 상태**: `Needs Revision` (수정 후 재검토)
- **리뷰어견**: TC 초안에 요구사항 누락, 모호성, Setup/Steps 중복, 그리고 통합 TC 포맷 위반 등 다수의 결함이 발견되어 승인이 불가합니다. 아래 9대 기준 채점 및 수정 가이드를 참고하여 재작성 바랍니다.

## 2. 9대 검토 기준 채점표
| 검토 기준 | Pass/Fail | 사유 |
| :--- | :---: | :--- |
| 1. 기대결과 모호성 | Fail | TC-INT-02(초안의 잘못된 ID)에 "100% 유지함" 이라는 모호한 표현 존재. |
| 2. 이중 단언(Double-Assert) 유무 | Fail | TC-02A의 Register Assert란에 값 대신 미적용 사유를 기재함. |
| 3. 정보 부족 항목 분리 | Pass | 명시된 검증 제외 항목 활용 양호. |
| 4. 추측성 검출 | Fail | TC-02A의 Risk Covered에 "하드웨어 에러 유발"이라는 가상의 위험을 추측하여 기재함. |
| 5. 요구사항 및 기준 추적성 | Fail | TC-INT-02에 Requirement ID 및 Source Evidence 누락. |
| 6. 자동화 적합성 | Fail | TC-01의 UI 표시 문자열 불일치 위험("HEAT" vs "난방") 및 `devices[1]` 인덱스/ID 매핑 모호함 존재. |
| 7. 테스트 독립성 | Fail | TC-02A에서 Setup에 "FAN 모드 적용"을 해놓고 Steps에서 다시 "FAN 모드 클릭"을 지시하여 테스트 전환 검증이 불가능해짐. |
| 8. 통합 TC 오염 검증 | Fail | TC-INT-02의 비대상 상태 불변 검증 로직이 불명확함 (Snapshot 부재). |
| 9. 중복 TC 통폐합 방어 | Pass | 중복된 TC는 없음. |

## 3. 환각 / 모호성 검출 리포트 (Needs Revision 피드백)

### [TC-01 피드백]
- **위반 Rule**: Major
- **수정 가이드**: 
  - UI Assert 값과 Register Assert 값을 분리할 것. (예: UI는 "난방", Register는 "HEAT")
  - `devices[1]`은 배열 인덱스 1인지 기기 ID 1인지 헷갈리므로 `devices.find(d => d.id === 1)` 포맷으로 구체화할 것.
  - Cleanup에 '기기 설정 전체 초기화 버튼(Reset)' 클릭 또는 명시적인 `load_clean_simulator` 호출을 명시할 것.

### [TC-02A 피드백]
- **위반 Rule**: Critical (근거 없는 Risk가 Expected Result에 전파될 위험)
- **수정 가이드**: 
  - Initial State를 `mode: COOL`로 설정하고, Steps에서 FAN 모드 버튼을 클릭하도록 Setup과 Steps의 역할을 분리할 것.
  - Register Assert 영역은 비워두거나 `[]`로 처리하고, `double_assert_policy`를 `UI-only`로 지정하여 미적용 사유를 시스템적으로 처리할 것.
  - Risk Covered에 기획되지 않은 하드웨어 에러 추측을 삭제하고, "UI와 내부 상태의 불일치 위험" 등으로 변경할 것.
  - (권고) FAN 모드 전환 자체를 검증하는 TC와 온도 비활성화를 검증하는 TC를 분리하는 것이 Atomic 원칙에 더 부합함.

### [TC-INT-02 피드백]
- **위반 Rule**: Major
- **수정 가이드**: 
  - Data Contract 필수 포맷(Initial State, Setup, Cleanup 등)을 완벽하게 채울 것.
  - 비대상 장비 불변 검증 시 "100% 유지"라는 단어를 삭제하고, "실행 전 Snapshot과 실행 후 값 비교" 방식으로 구체화할 것. (예: `before_devices[4].mode == after_devices[4].mode`)
