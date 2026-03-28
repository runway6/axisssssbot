import os, requests
from playwright.sync_api import sync_playwright

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            # 增加超时和简单的 Markdown 格式支持
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        except Exception as e:
            print(f"Telegram 发送异常: {e}")

def run():
    print("--- 启动过滤 Bug 任务版监控 (V4.0) ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 模拟大窗口确保卡片全部加载
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            print("正在访问 Axis Hub...")
            page.goto("https://hub.axisrobotics.ai/?tab=hub", wait_until="networkidle", timeout=60000)
            
            # 给页面 20 秒，让任务列表彻底刷出来
            print("等待列表渲染 (20s)...")
            page.wait_for_timeout(20000) 

            # --- 核心过滤逻辑 ---
            # 每一个任务卡片都有 "Difficulty" 加星星的标识
            # 我们直接统计页面上出现了几次 "Difficulty"
            task_cards = page.get_by_text("Difficulty")
            task_count = task_cards.count()
            
            print(f"当前页面共检测到 {task_count} 个任务。")

            # 如果任务数量 > 3，说明除了那个 Water Flower，还有别的任务上线了
            if task_count > 3:
                print(f"🚨 发现新任务！当前总计: {task_count} 个")
                send_tg(f"🚀 **Axis 任务预警：新单上线！**\n\n检测到当前有 **{task_count}** 个任务（已排除 Bug 练习任务）。\n\n[点击前往抢单](https://hub.axisrobotics.ai/?tab=hub)")
            else:
                # 只有 1 个（Water Flower）或 0 个时，保持静默
                print("✅ 检查完毕：目前只有 1 个 Bug 任务，保持静默。")
                
        except Exception as e:
            print(f"脚本运行出错: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
