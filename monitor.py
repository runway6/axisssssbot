import os
import requests
from playwright.sync_api import sync_playwright

# 配置信息
TARGET_URL = "https://hub.axisrobotics.ai/?tab=hub"
TG_TOKEN = os.environ.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

def send_tg(message):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("TG 配置错误")
        return
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=15)
    except:
        print("TG 发送失败")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 模拟一个大屏幕浏览器，确保元素都能渲染出来
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            print(f"开始访问: {TARGET_URL}")
            page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
            # 增加等待时间，确保动态加载的内容全部出来
            page.wait_for_timeout(20000) 

            # --- 新策略：检查特定的任务卡片选择器 ---
            # 1. 尝试寻找包含 "No tasks" 的 div 
            no_tasks_element = page.locator("div:has-text('No tasks')").first
            
            # 2. 检查这个 "No tasks" 元素是否真的在屏幕上显示
            is_no_tasks_visible = no_tasks_element.is_visible()

            print(f"检查结果 - 'No tasks' 是否可见: {is_no_tasks_visible}")

            if not is_no_tasks_visible:
                # 如果找不到 "No tasks"，我们再做一层保险：检查是否有任务卡片的特征类名
                # Axis 网站任务通常在类似 .task-card 或特定的 grid 布局里
                print("🚨 状态异常！未发现 'No tasks'，可能新任务已刷新！")
                send_tg(f"🚀 **Axis 任务预警**\n\n网页检测不到 'No tasks' 提示了，疑似新任务上线！\n\n[点击跳转]({TARGET_URL})")
            else:
                print("✅ 状态正常：页面依然显示 'No tasks'。")

        except Exception as e:
            print(f"运行出错: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
