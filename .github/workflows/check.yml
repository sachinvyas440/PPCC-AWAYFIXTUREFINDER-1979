name: Check Fixture List

on:
  schedule:
    - cron: "*/5 * * * *"
  workflow_dispatch: {}

permissions:
  contents: write

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Run checker
        env:
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
        run: python check.py

      - name: Commit updated state
        run: |
          git config user.name "fixture-watcher-bot"
          git config user.email "actions@users.noreply.github.com"
          git add state.json
          git diff --quiet --cached || git commit -m "Update state [skip ci]"
          git push
