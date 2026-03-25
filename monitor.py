import os
import requests
from playwright.sync_api import sync_playwright

# 配置信息
TARGET_URL = "https://hub.axisrobotics.ai/?tab=hub"
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

def send_tg(message):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("TG 配置错误：请检查 GitHub Secrets 中的 Token 和 Chat ID")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=15)
        print(f"Telegram 发送状态: {r.status_code}")
    except Exception as e:
        print(f"Telegram 发送异常: {e}")

def run():
    with sync_playwright() as p:
        # 模拟真实浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            print("正在同步网页数据...")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            # 强制等待 15 秒，确保内容（尤其是 "No tasks"）彻底加载出来
            page.wait_for_timeout(15000)

            # --- 核心监控逻辑 ---
            # 检查页面上是否还存在 "No tasks" 这个文本
            # 只要找不到这个词（visible 为 False），就代表可能有任务了
            no_tasks_visible = page.get_by_text("No tasks").first.is_visible()

            if not no_tasks_visible:
                print("🚨 [状态变更] 未发现 'No tasks' 字样，可能存在新任务！")
                send_tg(f"🚀 **Axis 新任务预警！**\n\n检测到网页状态已改变（不再显示 'No tasks'）。\n\n[点击立即抢单]({TARGET_URL})")
            else:
                print("✅ [监控中] 页面仍显示 'No tasks'，暂无新任务。")
            # --------------------

        except Exception as e:
            print(f"运行过程中出现错误: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
