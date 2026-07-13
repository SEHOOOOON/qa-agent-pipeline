# 🎯 알려진 한계점 및 아키텍처 트레이드오프 (Known Limitations & Trade-offs)

이 문서는 본 5-Agent QA 파이프라인을 실제 프로덕션(Production) 환경에 도입할 때 발생할 수 있는 구조적 한계점과, 이를 극복하기 위한 설계적 타협점(Trade-off)을 정리한 시니어 레벨의 아키텍처 회고록입니다.

---

### 📌 프로젝트 구현 현황 (V1 Implemented vs V2 Planned)

#### [V1 Implemented] 현재 구현 완료된 범위
- 사전 검증된 Playwright Helper 함수 사용
- 가상 Controller / Register Simulator 연동 및 검증
- Agent 2 (설계)와 Gate 2 (리뷰/통제)의 역할 분리
- 테스트별 상태 초기화(Setup/Cleanup)를 통한 독립성 보장

#### [V2 Planned] 향후 도입 계획
- Impact-based Test Selection (영향도 기반 테스트)
- 복수 모델 교차 검토 (Cross-Model Validation)
- 규칙 기반 Gate Validator (정적 룰 체크) 도입
- 실제 HIL(Hardware-in-the-Loop) 테스트 결과 연결
- Nightly Build / PR Build 실행 전략 분리

---

## 1. 다중 에이전트 파이프라인의 비용과 지연(Latency) 한계
* **한계점**: 파이프라인 실행 시 `Agent 1 ➔ Agent 2 ➔ Gate 2 ➔ Agent 3 ➔ Agent 4` 흐름으로 다수의 API 호출이 발생합니다. 매 빌드마다 모든 시나리오에 대해 LLM 기반 분석(Agent 1, 2, Gate 2)을 수행할 경우, 응답 지연과 토큰 비용 부담이 큽니다.
* **실무 방어 전략**: Agent 3(실제 Playwright 자동화)는 결정론적인 코드를 수행하므로 LLM 비용이 거의 없지만, 분석/리뷰 에이전트는 무겁습니다. 따라서 실무 적용 시, 정기 야간 빌드(Nightly Build)에만 전체 파이프라인을 가동하거나, 변경 사항이 발생한 특정 모듈에 대해서만 선택적으로 에이전트가 트리거되도록 **영향도 기반 테스트(Impact-based Testing)** 방식을 적용할 계획입니다.

## 2. Agent 3 (자동화 실행)의 '완전 자율성' 딜레마
* **한계점**: AI가 실행 시점마다 Playwright 코드를 동적으로 100% 자율 생성하게 두면, 동일한 요구사항에서도 Selector와 대기 방식이 매번 달라져 실행 결과의 재현성과 유지보수성이 현저히 낮아질 위험이 있습니다.
* **실무 방어 전략**: 이러한 불안정성(Flaky Risk)을 회피하기 위해, AI의 '완전 자율 코드 생성' 대신 **사전 검증된 Helper/Action 조합 기반의 제한적 코드 생성 전략**으로 아키텍처를 타협했습니다. 이는 AI의 자율성을 일정 부분 포기하는 대신, 테스트 실행의 결정론적(Deterministic) 안정성을 확보하기 위한 의도적인 트레이드오프입니다.

## 3. 가상 환경(Mock) 검증의 목적 한계
* **한계점**: 본 프로젝트의 테스트 대상(`virtual-controller.html`)은 브라우저 상의 가상 시뮬레이터입니다. 실제 기기와 연동될 때 발생하는 하드웨어 통신 지연, 패킷 유실 등 물리적 노이즈를 100% 모사할 수는 없습니다.
* **실무 방어 전략**: 본 프로젝트는 실제 H/W 고장 진단을 목표로 하지 않습니다. 가상 UI와 Register Simulator를 사용해 요구사항 누락, 제어 규칙 위반, UI/Register 불일치와 같은 **소프트웨어 상위 레이어의 결함 후보를 조기에 선별**하는 것을 목표로 합니다. 진짜 하드웨어 검증은 기존 HIL 테스트가 담당하도록 역할을 명확히 분리합니다.

## 4. "AI가 AI를 검수한다" (Gate 2)의 구조적 모순
* **한계점**: Agent 2가 작성한 설계를 Sub-Agent(Gate 2)가 검수하여 환각을 통제하는 구조이나, 두 에이전트가 동일한 기저 모델(LLM)을 사용할 경우 확증 편향(Confirmation Bias)을 공유하여 논리적 맹점을 똑같이 놓칠 위험이 있습니다.
* **실무 방어 전략**: Temperature를 0으로 설정하면 리뷰 결과의 재현성을 높일 수 있지만, 동일 모델이 가진 논리적 맹점 자체를 완벽히 제거하지는 못합니다. 따라서 V2에서는 Gate 2가 LLM 평가만 수행하지 않고, "Information Gap의 활용 여부", "Source ID 누락 여부" 등을 탐지하는 **결정론적 규칙 기반 Validator(Linter)** 로직과 결합하는 Hybrid 방식을 적용할 예정입니다.

## 5. LLM 판단과 결정론적 실행의 경계
* **한계점**: LLM에게 요구사항 분석뿐 아니라 최종적인 Pass/Fail 판정까지 맡기면, 동일한 실행 결과에 대해서도 AI의 기분에 따라 판정이 달라질 수 있습니다.
* **실무 방어 전략**: LLM은 "요구사항 정제", "테스트 관점 도출", "결과 설명 및 집계"만을 담당합니다. 실제 UI/Register의 Pass/Fail 여부는 Playwright의 **이중 단언(Double-Assert)** 이 담당하도록 분리했습니다. LLM의 자율적인 판단 범위를 줄임으로써, 동일 입력에서 동일 결과를 얻을 수 있는 재현성과 감사 가능성(Auditability)을 확보했습니다.
