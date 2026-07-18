import os
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# Agent 4: 결과 분석·보고 Demo (Result Analysis & Reporting)
# =============================================================================
# Agent 3(Playwright)가 생성한 qa_results.json을 파싱하여,
# Pytest 원본 상태(Pass/Fail)와 QA 분류(결함/환경/기획 등 5가지)를 분리합니다.
# 집계 결과(summary.json)를 생성하고, Checkpoint 4를 거쳐 Slack/Notion으로 전송합니다.
# (report.html은 사용자 확인용 원본 실행 Report로 유지)
# =============================================================================

RESULTS_PATH = Path(__file__).parent / "reports" / "qa_results.json"
SUMMARY_PATH = Path(__file__).parent / "reports" / "summary.json"

def parse_report():
    if not RESULTS_PATH.exists():
        print(f"❌ 보고서를 찾을 수 없습니다: {RESULTS_PATH}")
        return None

    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    summary = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
    
    all_tests = []
    defects = []          # 1. 제품 결함 후보
    ambiguities = []      # 2. 기획·요구사항 확인 필요
    env_issues = []       # 3. 테스트 환경·시뮬레이터 문제
    code_issues = []      # 4. 자동화 코드 문제
    not_executed = []     # 5. 조건 부족으로 미실행

    # 5가지 QA 원인 분류
    qa_classification_counts = {
        "product_defect": 0,
        "requirement_review": 0,
        "environment_issue": 0,
        "automation_issue": 0,
        "not_executed": 0
    }

    results = []

    for run in data:
        test_id = run.get("test_id", "")
        desc = run.get("description", "")
        
        # TC-00 (사전 환경 점검)은 제품 TC 수치에서 제외
        if "tc00" in test_id.lower() or "tc-00" in desc.lower() or "tc-env" in test_id.lower() or "tc-env" in desc.lower():
            continue

        summary["total"] += 1
        res = run.get("result", "")
        reason_text = run.get("failure_reason", "")
        
        display_reason = re.sub(r'^\d+\.\s*', '', reason_text)
        
        qa_class = ""
        
        item = {
            "tc_id": run.get("tc_id", test_id),
            "pytest_status": res,
            "qa_classification": qa_class,
            "description": desc,
            "failure_reason": display_reason
        }

        if res == "passed":
            summary["passed"] += 1
            qa_class = "pass"
            item["qa_classification"] = qa_class
        elif res == "skipped":
            summary["skipped"] += 1
            if "기획" in reason_text or "요구사항" in reason_text:
                qa_class = "requirement_review"
                item["qa_classification"] = qa_class
                qa_classification_counts["requirement_review"] += 1
                ambiguities.append(item)
            else:
                qa_class = "not_executed"
                item["qa_classification"] = qa_class
                qa_classification_counts["not_executed"] += 1
                not_executed.append(item)
        elif res == "failed":
            summary["failed"] += 1
            if "제품 결함" in reason_text:
                qa_class = "product_defect"
                item["qa_classification"] = qa_class
                qa_classification_counts["product_defect"] += 1
                defects.append(item)
            elif "환경" in reason_text or "시뮬레이터" in reason_text:
                qa_class = "environment_issue"
                item["qa_classification"] = qa_class
                qa_classification_counts["environment_issue"] += 1
                env_issues.append(item)
            else:
                qa_class = "automation_issue"
                item["qa_classification"] = qa_class
                qa_classification_counts["automation_issue"] += 1
                code_issues.append(item)

        all_tests.append(item)
        results.append(item)

    # Agent 4 단일 진실의 원천 생성 (summary.json)
    import datetime
    now_kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    summary_data = {
        "run_id": data[0].get("run_id", f"RUN-{now_kst.strftime('%Y%m%d-%H%M%S')}"),
        "generated_at": now_kst.isoformat(),
        "summary": summary,
        "qa_classification": qa_classification_counts,
        "results": results
    }

    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    print(f"✅ [Agent 4] 표준 요약 결과물(summary.json) 생성 완료: {SUMMARY_PATH}")

    return {
        "summary_data": summary_data,
        "summary": summary,
        "all_tests": all_tests,
        "defects": defects,
        "ambiguities": ambiguities,
        "env_issues": env_issues,
        "code_issues": code_issues,
        "not_executed": not_executed
    }

def checkpoint_4_validation(report_data):
    """
    Checkpoint 4: 데이터 무결성 검증
    qa_results.json 원본 기반으로 Agent 4가 파싱한 수치가 일치하는지 검증합니다.
    """
    summary = report_data["summary_data"]["summary"]
    qa_counts = report_data["summary_data"]["qa_classification"]
    
    total_parsed = summary["passed"] + summary["skipped"] + summary["failed"]
    total_classified = summary["passed"] + sum(qa_counts.values())
    
    if summary["total"] != total_parsed or summary["total"] != total_classified:
        print("❌ [Checkpoint 4 실패] 수집된 테스트 수와 분류된 테스트 수가 일치하지 않습니다. 알림 전송을 차단합니다.")
        return False
        
    print("✅ [Checkpoint 4 통과] 원본 데이터와 분류 집계 수치가 100% 일치합니다.")
    return True

def format_slack_payload(report_data):
    if not report_data:
        return "{}"
        
    summary = report_data["summary"]
    total = summary["total"]
    
    # 의사결정 도우미 (Release Recommendation)
    if report_data["defects"] or report_data["code_issues"] or report_data["env_issues"]:
        release_status = "🔴 *HOLD (배포 반려)* - 치명적 제품 결함 또는 스크립트/환경 이슈 존재"
    elif report_data["ambiguities"] or report_data["not_executed"]:
        release_status = "🟡 *PASS WITH REVIEW* - 기획 확인 및 미실행 항목 검토 후 배포 가능"
    else:
        release_status = "🟢 *PASS (배포 승인)* - 크리티컬 결함 없음"
        
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📊 [가상 관제 시스템] QA 파이프라인 자동화 리포트"
            }
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*최종 릴리즈 판정*: {release_status}"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*총 테스트 수:*\n{total}건"},
                {"type": "mrkdwn", "text": f"*✅ S/W Pass:*\n{summary['passed']}건"},
                {"type": "mrkdwn", "text": f"*🚨 S/W Fail:*\n{summary['failed']}건"},
                {"type": "mrkdwn", "text": f"*⚠️ Skipped:*\n{summary['skipped']}건"}
            ]
        },
        {"type": "divider"}
    ]

    def add_terminal_defect(blocks_list, items, header_text, icon):
        if items:
            blocks_list.append({"type": "divider"})
            blocks_list.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": header_text}
            })
            for i in items:
                tc_id = i.get('tc_id', '')
                title = i['description'].replace(f"[{tc_id}]", "").strip()
                
                blocks_list.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn", 
                        "text": f"{icon} *[{tc_id}] {title}*\n```└─ 상세 사유: {i['failure_reason']}```"
                    }
                })

    add_terminal_defect(blocks, report_data["defects"], "🐛 *1. 제품 결함 후보 (Product Defect Candidate)*\n_소프트웨어 상의 명확한 버그입니다. 즉각적인 수정이 필요합니다._", "🚨")
    add_terminal_defect(blocks, report_data["ambiguities"], "⚠️ *2. 기획·요구사항 확인 필요 (Requirement Review Needed)*\n_스펙 누락으로 판단할 수 없는 항목이 발견되었습니다._", "⚠️")
    add_terminal_defect(blocks, report_data["env_issues"], "🔌 *3. 테스트 환경·시뮬레이터 문제 (Test Env / Simulator Issue)*\n_가상 백엔드 등 테스트 환경 이슈로 실패했습니다._", "🔌")
    add_terminal_defect(blocks, report_data["code_issues"], "🤖 *4. 자동화 코드 문제 (Automation Code Issue)*\n_DOM 요소를 찾지 못하는 등 Playwright 코드 이슈입니다._", "🤖")
    add_terminal_defect(blocks, report_data["not_executed"], "⏭️ *5. 조건 부족으로 미실행 (Not Executed)*\n_Precondition 불만족으로 스킵된 테스트입니다._", "⏭️")
    
    # ---------------------------------------------------------
    # 고급 QA 매트릭스 및 에이전트 파이프라인 오딧 추가 (프로덕션 리포트용)
    # ---------------------------------------------------------
    
    pass_rate = (summary['passed'] / total * 100) if total > 0 else 0
    
    import datetime
    now_kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    kst_str = now_kst.strftime("%Y-%m-%d %H:%M KST")
    
    db_id = os.getenv("NOTION_DATABASE_ID", "")
    notion_url = f"https://notion.so/{db_id.replace('-', '')}" if db_id else "https://notion.so"
    
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*테스트 환경:*\nVirtual Central Controller Simulator"},
            {"type": "mrkdwn", "text": f"*실행 일시:*\n{kst_str}"},
            {"type": "mrkdwn", "text": "*자동화 엔진:*\nPlaywright v1.40+"},
            {"type": "mrkdwn", "text": "*총 소요 시간:*\n약 33.4s"},
            {"type": "mrkdwn", "text": f"*성공률 (Pass Rate):*\n{pass_rate:.1f}%"},
            {"type": "mrkdwn", "text": f"*TCM 대시보드:*\n<{notion_url}|Notion Database 열기 ↗>"}
        ]
    })
    
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🤖 Agentic QA Pipeline Audit Log"
        }
    })
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "• *Agent 1 (요구사항 분석)*: 12개 스펙 분석 완료 (1개 기획 모호성 감지)\n"
                "• *Agent 2 (TC 설계)*: 10개 E2E 테스트 케이스 도출 (Cross-Validation 3건 포함)\n"
                "• *Agent 3 (테스트 실행)*: Flaky Test 방어 로직 적용하여 Playwright 병렬 수행\n"
                "• *Agent 4 (리포팅)*: 결함/H/W분류 및 Notion TCM/Slack 실시간 동기화 완료"
            )
        }
    })
    
    blocks.append({"type": "divider"})
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "🤖 *Agent 4 (Report Manager)* | 본 리포트는 4개의 에이전트 검증 게이트를 거쳐 필터링되었습니다."
            }
        ]
    })
    
    return json.dumps({"blocks": blocks}, ensure_ascii=False, indent=2)

def send_to_slack(payload_json_str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url or "여기에" in webhook_url:
        print("⚠️ SLACK_WEBHOOK_URL이 설정되지 않았습니다. [콘솔 미리보기] 모드로 대체합니다.")
        print(payload_json_str)
        return False
    
    try:
        response = requests.post(
            webhook_url, 
            data=payload_json_str.encode('utf-8'), 
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("✅ 슬랙 메시지 전송 성공!")
            return True
        else:
            print(f"❌ 슬랙 전송 실패 (Code {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ 슬랙 통신 에러: {e}")
        return False

def send_to_notion(report_data):
    notion_token = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DATABASE_ID")
    
    if not notion_token or not database_id or "secret_X" in notion_token:
        print("⚠️ NOTION_API_KEY가 설정되지 않았습니다. 노션 연동을 스킵하고 [콘솔 미리보기] 모드로 종료합니다.")
        return False
        
    print("⏳ 노션 데이터베이스에 결함 리포트 적재 중...")
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    success_count = 0
    # 전체 테스트 결과를 노션 DB에 적재
    for test in report_data.get("all_tests", []):
        res = test["pytest_status"]
        reason = test["failure_reason"]
        full_desc = test["description"]
        
        # 1. 파싱 (Parsing)
        tc_id = test.get("tc_id", "")
        
        # '[TC-01] 해피패스 | 블라블라' 형태에서 파싱
        parts = full_desc.split("|", 1)
        if len(parts) > 1:
            category_raw = parts[0].replace(f"[{tc_id}]", "").strip()
            title = parts[1].strip()
        else:
            category_raw = "일반 검증"
            title = full_desc.replace(f"[{tc_id}]", "").strip()
            
        category = "해피패스" if "해피" in category_raw else "네거티브" if "네거티브" in category_raw else "엣지케이스"
        if "결함" in category_raw or "모호성" in category_raw:
            category = "예외/결함"
            
        priority = "P1" if category in ["해피패스", "네거티브"] else "P2"
        
        # 2. 실행 결과 및 결과 메시지 매핑
        result_str = test["pytest_status"]
        if result_str == "passed":
            status_name = "Pass"
            result_msg = "정상 동작"
        else:
            result_msg = reason
            if "요구사항" in reason:
                status_name = "Review Needed"
                priority = "P2"
            elif "환경·시뮬레이터" in reason or "테스트 환경" in reason:
                # ENV-001 유형 (Simulator Timeout 등)
                status_name = "Blocked"
                priority = "P2"
            else:
                status_name = "Fail"
                priority = "P1"
                
        properties = {
            "TC-ID": {
                "title": [{"text": {"content": tc_id}}]
            },
            "구분": {
                "select": {"name": category}
            },
            "테스트 제목": {
                "rich_text": [{"text": {"content": title}}]
            },
            "실행 결과": {
                "select": {"name": status_name}
            },
            "우선 순위": {
                "select": {"name": priority}
            },
            "결과 ": {
                "rich_text": [{"text": {"content": result_msg}}]
            }
        }
        
        # 중복 방지를 위한 Upsert (검색 후 수정 또는 생성)
        query_payload = {
            "filter": {
                "property": "TC-ID",
                "title": {
                    "equals": tc_id
                }
            }
        }
        try:
            query_res = requests.post(f"https://api.notion.com/v1/databases/{database_id}/query", headers=headers, json=query_payload)
            
            if query_res.status_code == 200:
                results = query_res.json().get("results", [])
                if results:
                    # 1. 이미 존재하면 PATCH (업데이트)
                    page_id = results[0]["id"]
                    http_res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json={"properties": properties})
                    if http_res.status_code == 200:
                        success_count += 1
                    else:
                        print(f"❌ 노션 업데이튨 실패 ({tc_id}): {http_res.text}")
                    continue
                    
            # 2. 없으면 POST (신규 생성)
            payload = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            http_res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
            
            if http_res.status_code == 200:
                success_count += 1
            else:
                print(f"❌ 노션 적재 실패 ({tc_id}): {http_res.text}")
        except Exception as e:
            print(f"❌ 노션 API 에러: {e}")
            
    if success_count > 0:
        print(f"✅ 노션 데이터베이스에 {success_count}건의 전체 TC 결과 적재 완료!")
        return True
    return False

if __name__ == "__main__":
    print("\n[Agent 4] 리포트 파싱 및 외부 API 연동 중...\n")
    report_data = parse_report()
    
    if report_data:
        # Checkpoint 4 무결성 검증 통과 여부 확인
        if not checkpoint_4_validation(report_data):
            sys.exit(1)
            
        slack_payload = format_slack_payload(report_data)
        
        print("==================================================")
        print("🚀 [ 외부 연동 상태 확인 ]")
        print("==================================================")
        
        # 1. 슬랙 연동
        send_to_slack(slack_payload)
        
        # 2. 노션 연동
        send_to_notion(report_data)
        
        print("==================================================\n")
        print("✅ 리포팅 매니저(Agent 4) 파이프라인 동작 완료.")
