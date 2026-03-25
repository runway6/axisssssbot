import os, requests
from playwright.sync_api import sync_playwright

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        except:
            print("Telegram 发送失败")

def run():
    print("--- 启动新版任务监控 (V3) ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # 访问目标网页
            page.goto("https://hub.axisrobotics.ai/?tab=hub", wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(15000) # 强制等待页面动态加载
            
            # 策略：直接获取页面文本，判断 "No tasks" 字符串是否存在
            content = page.content()
            
            if "No tasks" in content:
                print("✅ 检查结果：页面仍显示 'No tasks'，暂无新任务。")
            else:
                # 如果页面加载成功（包含 All Tasks）但没有 No tasks，则报警
                if "All Tasks" in content:
                    print("🚨 状态变更：未发现 'No tasks'，任务可能已上线！")
                    send_tg("🚀 **Axis 新任务提醒**\n\n检测到网页已不再显示 'No tasks'，快去看看！")
                else:
                    print("⚠️ 警告：页面似乎未完全加载或结构改变。")
                    
        except Exception as e:
            print(f"运行异常: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
