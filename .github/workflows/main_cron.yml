name: Axis_Progress_Monitor

on:
  schedule:
    - cron: '*/5 * * * *' # 每 5 分钟运行一次
  workflow_dispatch:

jobs:
  check-and-save:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Requests
        run: pip install requests

      - name: Run Monitor
        env:
          TG_TOKEN: ${{ secrets.TG_TOKEN }}
          TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
        run: python task_monitor.py # 这里已经修改对齐

      - name: Save memory back to Repo
        run: |
          git config --global user.name "AxisBot"
          git config --global user.email "bot@github.com"
          git add notified_ids.txt || exit 0
          git commit -m "更新已通知任务列表" || exit 0
          git push
