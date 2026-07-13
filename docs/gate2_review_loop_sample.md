# 🤖 Gate 2: AI 환각 통제 및 품질 리뷰 루프 샘플 (Review Loop Sample)

이 문서는 본 프로젝트의 핵심인 **"AI 환각(Hallucination)의 구조적 통제"** 과정을 보여주는 실제 구동 샘플입니다. 
단순히 Agent 2가 생성한 초안을 그대로 자동화 코드로 넘기지 않고, **Gate 2**가 깐깐한 QA 거버넌스 룰에 따라 반려(Needs Revision)하고 정제해 내는 과정을 증명합니다.

---

## 🛑 [Phase 1] Agent 2의 초안 (초기 생성물 - 환각 포함)
Agent 2가 도메인 룰(FAN 모드 시 온도 조절 차단)을 기반으로 처음 설계한 TC 초안입니다.
언뜻 보기엔 그럴싸하지만, 기획에 없는 UI 문구를 AI가 마음대로 추측(환각)하여 작성한 치명적 결함이 숨어 있습니다.

```yaml
# Agent 2 Draft (Rejected)
tc_id: "TC-02A_Rule2_송풍모드_온도조절_비활성화"
requirement_ids: ["DOMAIN-RULE-002"]
qa_criteria: ["배타 제어"]

steps: 
  - "FAN 모드 버튼 클릭"
expected_ui: 
  - "온도 표시 영역의 텍스트가 '---'로 변경된다."  # ❌ [문제점 1] 환각 (기획에 없는 문구 추측)
  - "온도 조절 버튼이 비활성화된다."
expected_register: 
  - "setTemp 변경 요청이 시스템에서 차단된다."      # ❌ [문제점 2] 모호성 (구체적 상태값 아님)
```

---

## 🚨 [Phase 2] Gate 2의 품질 리뷰 결과 (반려)
Gate 2 서브 에이전트가 QA Governance Rule에 따라 위 TC를 검토한 결과입니다.

- **최종 판정 상태**: `Needs Revision` (수정 후 재검토)
- **실무 유사성 평점**: 2.5 / 5.0

### 📋 8대 검토 기준 채점표 (발췌)
| 검토 기준 | 판정 | 이유 |
| :--- | :---: | :--- |
| 기대결과 명확성 | Fail | "요청이 시스템에서 차단된다"는 구체적인 코드로 변환할 수 없는 모호한 표현임. |
| 추측성 검출 | Fail | 온도 텍스트가 "---"로 바뀐다는 내용은 Agent 1의 [확정 정보]에 존재하지 않음. 명백한 AI 환각임. |
| 자동화 적합성 | Fail | Register의 어떤 변수가 어떻게 되는지 명확하지 않아 Playwright 매핑 불가. |

### 🛠️ 환각 / 모호성 검출 리포트 피드백
- **위반 Rule 종류**: Critical (환각 및 모호성)
- **수정 가이드**: 
  1. 기획에 없는 "---" 문자열 검증 스텝을 즉각 삭제하고 `검증 제외(Excluded)` 항목으로 분리할 것. 
  2. UI Assert는 `disabled` 상태만 확인하도록 축소할 것. 
  3. Register 차단 여부는 "Register-only Allowed" 예외 사유로 분류하거나, 값을 구체화할 것.

---

## ✅ [Phase 3] Agent 2의 수정본 (최종 승인)
Gate 2의 피드백을 수용한 뒤 Agent 2가 다시 생성한 2회차 수정본입니다.
환각이 제거되고 실무에서 즉시 코드로 자동화(Playwright)할 수 있는 수준으로 정제되었습니다.

```yaml
# Agent 2 Revised Draft (Approved)
tc_id: "TC-02A_Rule2_송풍모드_온도조절_비활성화"
requirement_ids: ["DOMAIN-RULE-002"]
qa_criteria: ["도메인 특화 배타 제어"]

steps: 
  - "FAN 모드 버튼 클릭"
expected_ui: 
  - "온도 조절 영역(Up/Down 버튼 등)이 `disabled` 처리됨."  # ✅ 환각 제거 및 상태 단언
expected_register: 
  - "UI-only Allowed 예외 적용 (상태 입력 UI 차단 여부 확인이므로 Register 갱신 불필요)" # ✅ 명확한 예외 사유 기재
excluded_assertions:
  - "FAN 모드의 온도 표시 문자열 (기획 미정의로 검증 제외)"  # ✅ 모르는 것은 모른다고 분리
```

### 🎯 Gate 2 최종 판정
- **최종 판정 상태**: `Approved`
- **의견**: Critical/Major 위반 사항이 모두 해소됨. 상상으로 만들어낸 Expected Result가 제거되었고, 명확한 단언(Assert) 기준이 성립하여 Agent 3 (자동화 봇)로 이관 가능.
