# Agent 2 (TC 아키텍트) 설계 산출물 샘플

### [그룹 A: Atomic TCs (개별 관제점 독립 검증)]
1. **TC_ID 및 제목**: TC-02A_송풍모드_온도조절_비활성화
2. **Priority & Type**: High / Negative (Rule 2 예외 차단)
3. **Purpose & Preconditions**: 송풍 모드에서는 사용자가 온도를 조작할 수 없도록 강제한다.
4. **Steps**:
   - 장치 카드 선택 후 제어 패널 진입
   - 'FAN(송풍)' 모드 클릭
5. **Expected Results**:
   - **UI Assert**: 온도 표시가 "---"로 변경되고, UP/DOWN 버튼이 `disabled` 처리된다.
   - **Register Assert**: `devices[id].mode`가 "FAN"으로 갱신되며 `setTemp` 변경 요청이 시스템에서 차단된다.

### [그룹 B: Integration TCs (전체 관제점 일괄 적용 E2E 정합성 검증)]
1. **TC_ID 및 제목**: TC-INT-01_멀티제어_전체상태_E2E_정합성
2. **Priority & Type**: Critical / E2E Integration
3. **Purpose & Preconditions**: 복수 기기를 선택하고 다수의 상태값(난방, 24도)을 동시 적용 시 시스템 오염(Race Condition)이 없는지 확인.
4. **Steps**:
   - 1번, 2번, 3번 장치 카드 다중 선택
   - 운전모드 'HEAT', 설정온도 '24°C' 동시 세팅 후 [적용] 클릭
5. **Expected Results**:
   - **UI Assert**: 3개 카드의 모드 텍스트가 모두 '난방', 온도가 '24.0°C'로 동기화.
   - **Register Assert**: `devices[0,1,2]`의 객체 속성이 모두 `{mode: "HEAT", setTemp: 24}`로 100% 동기화됨. (이중 단언 통과)
