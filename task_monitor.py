import os, requests
from playwright.sync_api import sync_playwright

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            # 增加超时检测，防止网络卡死
            res = requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=15)
            print(f"Telegram 发送结果: {res.status_code}")
        except Exception as e:
            print(f"Telegram 发送异常: {e}")
    else:
        print("错误：未在 GitHub Secrets 中找到 TG_TOKEN 或 TG_CHAT_ID")

def run():
    print("--- 启动新版任务监控 (V3.1) ---")
    
    # 【测试行】只要运行，就先发一条电报证明机器人活着
    # 如果你想安静点，测试成功后可以删掉下面这一行
    send_tg("🔔 **监控运行报告**：机器人已成功连接网页，正在为您站岗！")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        try:
            print("正在打开 Axis 官网...")
            page.goto("https://hub.axisrobotics.ai/?tab=hub", wait_until="networkidle", timeout=60000)
            
            # 关键：给页面 15 秒加载动态任务数据
            print("等待数据渲染 (15秒)...")
            page.wait_for_timeout(15000) 
            
            # 获取页面全文本
            content = page.content()
            
            # 逻辑：如果页面加载出来了，但找不到 "No tasks"
            if "No tasks" in content:
                print("✅ 结果：网页依然显示 'No tasks'，暂无新任务。")
            else:
                # 二次确认：页面必须已经加载出任务列表的基础文字
                if "All Tasks" in content:
                    print("🚨 状态变更：未发现 'No tasks'，疑似有新任务！")
                    send_tg("🚀 **Axis 任务紧急预警！**\n\n检测到网页已不再显示 'No tasks'！\n\n[立即点击抢单](https://hub.axisrobotics.ai/?tab=hub)")
                else:
                    print("⚠️ 警告：页面加载可能不完整（没看到 All Tasks），跳过报警。")
                    
        except Exception as e:
            print(f"运行出错: {e}")
            # 如果是网络报错，也发个通知提醒你检查
            # send_tg(f"❌ 监控脚本运行出错: {str(e)}") 
        finally:
            browser.close()

if __name__ == "__main__":
    run()
