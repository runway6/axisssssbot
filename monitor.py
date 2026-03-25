import os, requests
from playwright.sync_api import sync_playwright

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg})

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://hub.axisrobotics.ai/?tab=hub", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(15000) # 多等会儿确保加载完
            
            # 这里的逻辑：只要页面上【没有】出现 "No tasks" 几个字，就报警
            # 使用 count() 避开 strict mode 错误
            no_task_count = page.get_by_text("No tasks").count()
            
            print(f"找到 No tasks 的数量: {no_task_count}")
            
            if no_task_count == 0:
                print("🚨 没找到 No tasks，任务可能来了！")
                send_tg("🚀 Axis Robotics 提醒：网页上没看到 'No tasks'，快去看看是不是出新任务了！")
            else:
                print("✅ 还在显示 No tasks，继续监控中。")
        except Exception as e:
            print(f"出错啦: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
