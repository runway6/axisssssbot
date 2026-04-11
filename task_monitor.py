import os
import requests

def send_tg(msg):
    token = os.environ.get("TG_TOKEN")
    chat_id = os.environ.get("TG_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}, timeout=15)
        except Exception as e:
            print(f"TG 发送异常: {e}")

def run():
    api_url = "https://hub.axisrobotics.ai/api/tasks"
    memory_file = "notified_ids.txt"
    print(f"--- 启动任务进度深度扫描 (V7.0) ---")

    # 1. 加载已经通知过的任务 ID，防止重复轰炸
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            notified_ids = set(f.read().splitlines())
    else:
        notified_ids = set()
    
    try:
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        all_tasks = data.get("tasks", [])
        new_active_tasks = []

        # 2. 核心逻辑：遍历所有任务，寻找进度不足 100% 的
        for task in all_tasks:
            task_id = str(task.get("id"))
            progress = task.get("progress", 100.0)
            task_name = task.get("name", "未知任务")

            # 如果进度小于 100 且 之前没通知过这个 ID
            if progress < 100.0 and task_id not in notified_ids:
                new_active_tasks.append(f"• {task_name} (当前进度: {progress}%)")
                notified_ids.add(task_id)

        # 3. 发送预警
        if new_active_tasks:
            print(f"🚨 发现 {len(new_active_tasks)} 个未满 100% 的新任务！")
            tasks_str = "\n".join(new_active_tasks)
            msg = (
                f"🔥 **Axis 实时新任务预警！**\n\n"
                f"检测到以下任务进度不足 100%，疑似刚上线：\n\n"
                f"{tasks_str}\n\n"
                f"[立即前往抢单](https://hub.axisrobotics.ai/?tab=hub)"
            )
            send_tg(msg)
            
            # 更新记忆文件
            with open(memory_file, "w") as f:
                f.write("\n".join(notified_ids))
            print("✅ 记忆已更新。")
        else:
            print("✅ 扫描完毕：所有任务均已达 100% 或已通知，保持静默。")

    except Exception as e:
        print(f"扫描出错: {e}")

if __name__ == "__main__":
    run()
