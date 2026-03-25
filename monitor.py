import os
import requests
from playwright.sync_api import sync_playwright

# 配置信息
TARGET_URL = "https://hub.axisrobotics.ai/?tab=hub"
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

def send_tg(message):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(10000) # 等待加载

            # 判断逻辑：页面有 "All Tasks" 标识但没有 "No tasks" 文本
            is_ready = page.get_by_text("All Tasks").is_visible()
            no_tasks = page.get_by_text("No tasks").is_visible()

            if is_ready:
                if not no_tasks:
                    send_tg(f"🚀 **检测到新任务！**\n页面当前已不是 'No tasks' 状态。\n[立即前往查看]({TARGET_URL})")
                    print("通知已发送")
                else:
                    print("暂无任务")
            else:
                print("页面未正常加载")
        except Exception as e:
            print(f"出错: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
