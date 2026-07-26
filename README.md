<div align="center">

[![포트폴리오 웹페이지](https://img.shields.io/badge/포트폴리오_웹페이지_보기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/)
[![가상 관제 화면](https://img.shields.io/badge/가상_모의_관제_화면-58A6FF?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)
[![GitHub](https://img.shields.io/badge/GitHub_Repository-181717?style=for-the-badge&logo=github)](https://github.com/SEHOOOOON/qa-agent-pipeline)

**AI-assisted 4-Agent QA 검증 워크플로 + Playwright 자동화 파이프라인**
기획서 분석부터 테스트 시나리오 설계, Playwright 자동 실행, 비통과 원인 분석과 릴리즈 판단까지
QA 전 과정을 4단계로 단순화하여 연결한 프로젝트입니다.

</div>

---

## 👨‍💻 경력 요약

| 기간 | 회사 | 직책 | 주요 업무 |
|------|------|------|-----------|
| 2024.11–현재 | 테스트코윈 | ES 제어 QE팀 대리 (SQA) | 중앙제어·ES 제어 시스템 SQA, 통신 프로토콜 연동 및 회귀 검증 |
| 2021.12–2023.08 | ㈜빌트온 | 데이터 센터 사원 (Data QA/QC) | Python Data QC 로직 개발, 데이터 정합성 검수 및 모니터링 |

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

# 영상용 정상 회귀 12건 및 MP4 재생성
python -m pytest demo_tests/test_demo_regression.py -q --browser chromium -o "addopts="
python record_demo.py
```

- 통합 Run: 전체 13건 / Passed 8 / Failed 3 / Skipped 2
- 영상용 정상 회귀: 통합 분류 보고서를 덮어쓰지 않는 별도 12건 스위트이며, 모두 통과한 실행 로그를 Section 8 영상에 사용합니다.
- `python record_demo.py`: Agent 1~4 Workflow Demo, 실제 LOCK 관제점 제어 차단, `12 passed` 로그, Notion TC 테이블과 Slack 최신 알림 캡처를 순서대로 연결해 `assets/playwright_pipeline_demo.mp4`를 생성합니다.
- `python notify_agent.py`: 기본 Dry-run. Agent 4·Checkpoint 4 산출물과 Slack/Notion Payload만 생성하며 외부 전송은 하지 않습니다.
- `python notify_agent.py --send`: 환경변수가 설정된 경우에만 Slack Webhook 및 Notion TC-ID Upsert를 실제 수행합니다.
- 실제 전송 환경변수: `SLACK_WEBHOOK_URL`, `NOTION_API_KEY`, `NOTION_DATA_SOURCE_ID` (Notion API `2026-03-11`).
- 실행 결과가 `FAILED`여도 데이터 정합성이 맞으면 Checkpoint 4는 `VALIDATED`, Release는 `HOLD`가 됩니다.

<div align="center">

*Built with AI-assisted QA Workflow · Playwright/Pytest · Slack/Notion API Adapter*

[![시뮬레이터 바로가기](https://img.shields.io/badge/시뮬레이터_바로가기-a855f7?style=for-the-badge&labelColor=08060f)](https://SEHOOOOON.github.io/qa-agent-pipeline/virtual-controller.html)

</div>
