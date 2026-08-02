<div align="center">

[![포트폴리오 웹페이지](https://img.shields.io/badge/포트폴리오_웹페이지_보기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/)
[![가상 관제 화면](https://img.shields.io/badge/가상_모의_관제_화면-58A6FF?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)
[![GitHub](https://img.shields.io/badge/GitHub_Repository-181717?style=for-the-badge&logo=github)](https://github.com/SEHOOOOON/qa-agent-pipeline)

**AI-assisted 4-Agent QA 검증 워크플로 + Playwright 자동화 파이프라인**
기획서 분석부터 테스트 시나리오 설계, Playwright 자동 실행, 비통과 원인 분석과 릴리즈 판단까지
QA 전 과정을 4단계로 단순화하여 연결한 프로젝트입니다.

</div>

---


---

## 1. 프로젝트 정의 및 핵심 목표

이 프로젝트는 기존 중앙제어 시스템에 신규 기능이나 변경 요구사항이 접수됐을 때 작동하는 **AI-assisted QA 변경 검증 파이프라인**입니다.

> **💡 핵심 철학**
> AI가 사람을 대신해 모든 걸 완벽히 알아서 판정하는 것이 아닙니다.
> * **AI**: 요구사항 분석과 테스트 설계 보조
> * **Playwright**: 승인된 테스트의 결정적 실행
> * **Checkpoint**: 잘못된 산출물의 다음 단계 전달 차단
> * **사람**: 실무 환경에서 최종 승인과 예외 판단

중앙제어 QA 경험에서 정립한 품질 기준을 구조화하고, 근거가 부족하거나 신뢰할 수 없는 결과가 다음 단계로 전달되지 않도록 단계별 품질 게이트를 촘촘히 둔 것이 핵심입니다.

---

## 2. 메인 4단계 프로세스

내부 로직은 고도로 복잡하지만, 외부에 보여지는 프로세스는 매우 단순한 4단계로 구성됩니다.

### 1. 요구사항 정리
* 확정 정보와 정보 부족(Requirement Gap)을 정확히 구분하여 도출.
* *[✓ 테스트 가능한 범위 검토 (Checkpoint 1)]*

### 2. 테스트케이스 설계
* 3-Tier QA 기준(공통/도메인/기능)을 적용하여 TC를 설계.
* *[✓ 근거·누락·독립성 검토 (Checkpoint 2)]*

### 3. 자동화 실행
* 승인된 TC를 Playwright로 실행하고 Pytest 원본 결과를 저장.
* *[✓ 환경·실행 결과 유효성 검토 (Checkpoint 3)]*

### 4. 결과 분석·보고
* 비통과 원인을 5가지로 분류하고 릴리즈 권고(PASS/HOLD) 판단.
* *[✓ Report·JSON·보고값 일치 검토 (Checkpoint 4)]*

---

## 3. 핵심 차별점 3가지

1. **3-Tier QA 기준 도입**: 요구사항에만 의존하지 않고 공통/도메인/기능별 숨겨진 위험을 교차 점검합니다.
2. **UI·내부 상태 Double-Assert**: 화면(UI)에 속지 않고 백엔드(Register/Memory)의 상태값까지 교차 검증합니다.
3. **보고 전 결과 정합성 검증**: AI의 보고서가 실제 Pytest 원본 결과와 어긋나지 않았는지 검사(Checkpoint 4)한 후 릴리즈를 결정합니다.

---

## 4. 📚 내부 아키텍처 및 실무 도입 상세 문서

프로세스의 세부 동작 원리, 데이터 흐름, 실무 도입 시 한계점에 대한 상세한 문서는 아래 링크에서 확인하실 수 있습니다.

*   [**`docs/architecture/QA_PIPELINE_ARCHITECTURE.md`**](docs/architecture/QA_PIPELINE_ARCHITECTURE.md)
    *   Agent와 Checkpoint의 상세 역할, 12단계 흐름, 최종 판정 SSOT 구조 설명
*   [**`docs/samples/traceability_matrix.md`**](docs/samples/traceability_matrix.md)
    *   요구사항·TC·자동화 함수·Finding·릴리즈 판정 추적성
*   [**`docs/architecture/agent2_3tier_qa_criteria.md`**](docs/architecture/agent2_3tier_qa_criteria.md)
    *   3-Tier 세부 체크리스트와 요구사항 충돌 시 우선순위 해결 원칙
*   [**`docs/architecture/production_adoption_considerations.md`**](docs/architecture/production_adoption_considerations.md)
    *   실무 도입 4단계, AI 비결정성 통제, 중복 이슈(Upsert) 방어, 보안 대책

---

## 5. 실행 및 검증

```bash
# 통합 분류 파이프라인
python -m pytest
python notify_agent.py
python reports/validate_outputs.py

```

- 통합 Run: 전체 13건 / Passed 8 / Failed 3 / Skipped 2
- `python notify_agent.py`: 기본 Dry-run. Agent 4·Checkpoint 4 산출물과 Slack/Notion Payload만 생성하며 외부 전송은 하지 않습니다.
- `python notify_agent.py --send`: 환경변수가 설정된 경우에만 Slack Webhook 및 Notion TC-ID Upsert를 실제 수행합니다.
- 실제 전송 환경변수: `SLACK_WEBHOOK_URL`, `NOTION_API_KEY`, `NOTION_DATA_SOURCE_ID` (Notion API `2026-03-11`).
- 실행 결과가 `FAILED`여도 데이터 정합성이 맞으면 Checkpoint 4는 `VALIDATED`, Release는 `HOLD`가 됩니다.
---

## 6. 파일·폴더 구성

### 웹페이지 및 실행 설정

| 파일 | 용도 |
|------|------|
| `index.html` | 오세훈 QA 포트폴리오의 대표 홈 페이지 |
| `project.html` | Multi-Agent QA Workflow의 아키텍처·TC·실행 결과·영상·산출물을 설명하는 프로젝트 상세 페이지 |
| `virtual-controller.html` | Playwright 자동화 대상인 가상 중앙제어 시스템 시뮬레이터 |
| `notify_agent.py` | Agent 4 결과 집계, 5가지 원인 분류, Checkpoint 4 정합성 검증 및 Slack·Notion Payload 생성 |
| `pytest.ini` | Pytest 실행 옵션과 HTML 보고서 생성 경로 설정 |
| `requirements.txt` | 테스트·보고 파이프라인 실행에 필요한 Python 패키지 목록 |
| `.gitignore` | 실행 중 생성되는 결과, 보안 정보와 로컬 전용 도구의 Git 추적 제외 규칙 |
| `README.md` | 프로젝트 목표, 구조, 실행 방법과 파일 구성 안내 |

### 자동화 테스트

| 파일 | 용도 |
|------|------|
| `tests/test_controller.py` | 모드·온도·잠금·장애·다중 제어 검증과 5가지 비통과 분류 사례를 포함한 13건의 Playwright 테스트 |
| `tests/conftest.py` | 브라우저 실행 조건, 테스트 결과 수집, `qa_results.json` 및 Pytest HTML 보고서 생성을 담당하는 공통 설정 |

### Agent 4 및 Checkpoint 4 결과

| 파일 | 용도 |
|------|------|
| `reports/report.html` | Pytest 원본 실행 보고서로, Agent 4 결과 분석과 Checkpoint 4 대조의 기준 자료 |
| `reports/qa_results.json` | 13건의 TC별 상태·실패 사유·분류 결과를 구조화한 원본 데이터 |
| `reports/agent4_summary.json` | Agent 4가 집계한 통과·실패·미실행 수치, 5가지 원인 분류와 릴리즈 판단 결과 |
| `reports/checkpoint4_validation.json` | Report·JSON·Run ID·분류 수치의 일치 여부를 검증한 Checkpoint 4 결과 |
| `reports/validate_outputs.py` | 보고서·JSON·포트폴리오 표의 TC 수치와 매핑이 일치하는지 재검증하는 도구 |

### 포트폴리오 자산

| 파일 | 용도 |
|------|------|
| `assets/playwright_pipeline_demo.mp4` | Agent 1~4 흐름, Playwright 제어, `12 passed` 로그와 Notion·Slack 결과를 보여주는 구현 영상 |

### 설계·면접·샘플 문서

| 파일 | 용도 |
|------|------|
| `docs/architecture/QA_PIPELINE_ARCHITECTURE.md` | Agent와 Checkpoint의 역할, 데이터 흐름과 최종 판정 구조 설명 |
| `docs/architecture/agent2_3tier_qa_criteria.md` | 공통 QA·중앙제어 도메인·기능별 기준으로 구성된 3-Tier TC 설계 원칙 |
| `docs/architecture/production_adoption_considerations.md` | 실제 서비스 적용 단계, AI 비결정성 통제, 중복 전송과 보안 고려사항 |
| `docs/interview/BUSINESS_ROI_AND_IMPACT.md` | 자동화 파이프라인의 업무 효과와 비즈니스 관점 설명 자료 |
| `docs/interview/PORTFOLIO_INTERVIEW_POINTS.md` | 프로젝트 의도, 한계와 예상 기술 면접 질문에 대한 답변 가이드 |
| `docs/prompts/agent1_requirement_analyst.md` | Agent 1의 요구사항 확정·추정·정보 부족 분리 규칙 |
| `docs/prompts/agent2_tc_designer.md` | Agent 2의 테스트케이스 설계 역할과 출력 기준 |
| `docs/prompts/checkpoint2_tc_reviewer.md` | Checkpoint 2의 TC 승인·수정 요청·실행 제외 심사 기준 |
| `docs/samples/agent1_output_sample.md` | Agent 1 요구사항 분석 결과 예시 |
| `docs/samples/agent2_tc_draft.md` | Checkpoint 검토 전 Agent 2 테스트케이스 초안 |
| `docs/samples/agent2_tc_revised.md` | Checkpoint 2 피드백을 반영한 테스트케이스 수정본 |
| `docs/samples/checkpoint2_review_before.md` | 품질 기준 미충족 TC의 반려 근거 예시 |
| `docs/samples/checkpoint2_review_after.md` | 수정 TC의 품질 기준 충족 및 승인 결과 예시 |
| `docs/samples/traceability_matrix.md` | 요구사항·TC ID·자동화 함수·Finding·릴리즈 판정을 연결한 추적성 표 |

### 로컬 전용 파일(GitHub 미공개)

| 파일 | 용도 |
|------|------|
| `record_demo.py` | 구현 영상 MP4를 다시 제작할 때만 사용하는 로컬 녹화 스크립트 |
| `demo_tests/test_demo_regression.py` | 영상에 표시되는 정상 회귀 `12 passed` 장면을 만들기 위한 로컬 테스트 스위트 |
| `.env` | Slack·Notion 연동 인증정보를 보관하는 로컬 환경변수 파일 |

<div align="center">

*Built with AI-assisted QA Workflow · Playwright/Pytest · Slack/Notion API Adapter*

[![시뮬레이터 바로가기](https://img.shields.io/badge/시뮬레이터_바로가기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

</div>
