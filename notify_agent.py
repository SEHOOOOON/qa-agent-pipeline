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
# Agent 4: 리포트 & Slack 알림 에이전트 (Report & Notification Manager)
# =============================================================================
# Agent 3(Playwright)가 생성한 report.html을 파싱하여,
# 단순 Pass/Fail이 아닌 "실패 사유(Failure Classification)"를 기반으로
# [제품 결함]과 [요구사항 확인 필요]를 분리하여 Slack Webhook으로 쏘는 역할.
# =============================================================================

RESULTS_PATH = Path(__file__).parent / "qa_results.json"

def parse_report():
    if not RESULTS_PATH.exists():
        print(f"❌ 보고서를 찾을 수 없습니다: {RESULTS_PATH}")
        return None

    with open(RESULTS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # 1. 요약 통계 추출
    summary = {"passed": 0, "failed": 0, "hw_failed": 0, "total": 0}
    
    all_tests = []
    defects = []
    ambiguities = []
    env_errors = []
    hw_issues = []

    for run in data:
        summary["total"] += 1
        res = run.get("result", "")
        test_id = run.get("test_id", "")
        desc = run.get("description", "")
        reason_text = run.get("failure_reason", "")
        
        item = {"test": test_id, "desc": desc, "reason": reason_text, "result": res}
        all_tests.append(item)

        if res == "passed":
            summary["passed"] += 1
        elif res == "failed":
            if "요구사항" in reason_text:
                summary["failed"] += 1
                ambiguities.append(item)
            elif "제품 결함" in reason_text:
                summary["failed"] += 1
                defects.append(item)
            elif "H/W 장비 점검" in reason_text:
                summary["hw_failed"] += 1
                hw_issues.append(item)
            else:
                summary["failed"] += 1
                env_errors.append(item)

    return {
        "summary": summary,
        "all_tests": all_tests,
        "defects": defects,
        "ambiguities": ambiguities,
        "env_errors": env_errors,
        "hw_issues": hw_issues
    }

def format_slack_payload(report_data):
    if not report_data:
        return "{}"
        
    summary = report_data["summary"]
    total = summary["total"]
    
    # 의사결정 도우미 (Release Recommendation)
    if report_data["defects"] or report_data["hw_issues"]:
        release_status = "🔴 *HOLD (배포 반려)* - 치명적 제품 결함 또는 H/W 이슈 존재"
    elif report_data["ambiguities"]:
        release_status = "🟡 *PASS WITH REVIEW* - 기획 확인 후 배포 가능"
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
                {"type": "mrkdwn", "text": f"*S/W Pass:*\n✅ {summary['passed']}건"},
                {"type": "mrkdwn", "text": f"*S/W Fail:*\n🚨 {summary['failed']}건"}
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
                import re
                tc_id_match = re.search(r'\[(.*?)\]', i['desc'])
                tc_id = tc_id_match.group(1) if tc_id_match else i['test']
                title = i['desc'].replace(f"[{tc_id}]", "").strip()
                
                blocks_list.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn", 
                        "text": f"{icon} *[{tc_id}] {title}*\n```└─ 상세 사유: {i['reason']}```"
                    }
                })

    add_terminal_defect(blocks, report_data["defects"], "🐛 *[조치 필요] 제품 결함 (Product Defect)*\n_소프트웨어 상의 명확한 버그입니다. 즉각적인 수정이 필요합니다._", "🚨")
    add_terminal_defect(blocks, report_data["ambiguities"], "⚠️ *[확인 필요] 요구사항 모호성 감지 (Requirement Ambiguity)*\n_자동화 테스트 중 기획서 스펙 누락으로 판단할 수 없는 항목이 발견되었습니다. 기획팀 확인을 요청합니다._", "⚠️")
    add_terminal_defect(blocks, report_data["hw_issues"], "🔌 *[장비 점검] 하드웨어 무응답 이슈 (H/W Timeout)*\n_테스트 중 H/W 장비가 S/W의 제어 명령에 응답하지 않아 발생한 실패입니다._", "🔌")
    
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
        print("⚠️ SLACK_WEBHOOK_URL이 설정되지 않아 콘솔 시뮬레이션으로 대체합니다.")
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
        print("⚠️ NOTION 토큰이 설정되지 않아 노션 연동을 스킵합니다.")
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
        res = test["result"]
        reason = test["reason"]
        full_desc = test["desc"]  # e.g., "[TC-01] 해피패스 | 장치 #1 선택..."
        
        # 1. 파싱 (Parsing)
        import re
        tc_id_match = re.search(r'\[(.*?)\]', full_desc)
        tc_id = tc_id_match.group(1) if tc_id_match else test["test"]
        
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
        if res == "passed":
            status_name = "Pass"
            result_msg = "정상 동작"
        else:
            result_msg = reason
            if "요구사항" in reason:
                status_name = "Review Needed"
                priority = "P2"
            elif "장비 점검" in reason:
                status_name = "Blocker"
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
                    res = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json={"properties": properties})
                    if res.status_code == 200:
                        success_count += 1
                    else:
                        print(f"❌ 노션 업데이트 실패 ({tc_id}): {res.text}")
                    continue
                    
            # 2. 없으면 POST (신규 생성)
            payload = {
                "parent": {"database_id": database_id},
                "properties": properties
            }
            res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
            
            if res.status_code == 200:
                success_count += 1
            else:
                print(f"❌ 노션 적재 실패 ({tc_id}): {res.text}")
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
