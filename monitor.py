import os, requests
from playwright.sync_api import sync_playwright

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg}, timeout=10)
        except:
            print("TG发送失败")

def run():
    print("--- 启动全新逻辑版本 ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://hub.axisrobotics.ai/?tab=hub", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(15000)
            
            # 统计包含 No tasks 文本的元素个数
            content = page.content()
            if "No tasks" in content:
                print("✅ 还在显示 No tasks，暂无新任务。")
            else:
                print("🚨 状态变更！没看到 No tasks！")
                send_tg("🚀 Axis 提醒：网页不再显示 'No tasks'，快去看任务！")
        except Exception as e:
            print(f"出错: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
