import os, requests
from playwright.sync_api import sync_playwright

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        except Exception as e:
            print(f"Telegram 发送异常: {e}")

def run():
    print("--- 启动过滤 Bug 任务版监控 (V4.2) ---")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        
        try:
            print("正在访问 Axis Hub...")
            page.goto("https://hub.axisrobotics.ai/?tab=hub", wait_until="networkidle", timeout=60000)
            
            print("等待列表渲染 (20s)...")
            page.wait_for_timeout(20000) 

            # 核心过滤逻辑：统计 "Difficulty" 出现次数
            task_cards = page.get_by_text("Difficulty")
            task_count = task_cards.count()
            
            print(f"当前页面共检测到 {task_count} 个任务。")

            # 如果总任务数 x > 3，说明有新任务
            if task_count > 3:
                new_tasks_actual = task_count - 3  # 计算实际新增数量 (x-3)
                print(f"🚨 发现新任务！当前总计: {task_count} 个，实际新增: {new_tasks_actual} 个")
                
                # 发送格式化消息
                msg = (
                    f"🚀 **Axis 任务预警：新单上线！**\n\n"
                    f"当前总任务数：{task_count} 个\n"
                    f"✨ **实际新增任务：{new_tasks_actual} 个**\n\n"
                    f"[点击前往抢单](https://hub.axisrobotics.ai/?tab=hub)"
                )
                send_tg(msg)
            else:
                # 只有 3 个或更少时，判定为常驻 Bug/练习任务，保持静默
                print(f"✅ 检查完毕：当前有 {task_count} 个任务，未达到报警阈值，保持静默。")
                
        except Exception as e:
            print(f"脚本运行出错: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
