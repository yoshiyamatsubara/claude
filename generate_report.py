#!/usr/bin/env python3
"""
毎朝6時に実行される、コミック・ウェブトゥーン・アニメ業界レポート生成スクリプト
"""

import anthropic
import smtplib
import os
import json
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# 日本時間
JST = timezone(timedelta(hours=9))
today = datetime.now(JST).strftime("%Y年%m月%d日")

SYSTEM_PROMPT = """あなたはコミック・ウェブトゥーン・アニメ業界の専門アナリストです。
毎朝、最新情報を調査し、日本語で詳細なレポートを作成します。

以下のフォーマットで必ずHTMLで出力してください（```htmlは不要、HTMLそのまま出力）。
スタイルはインラインで書いてください。"""

USER_PROMPT = f"""今日（{today}）のコミック・ウェブトゥーン・アニメ業界の最新情報を調査して、以下の形式でレポートを作成してください。

調査対象：
- コミック（日本マンガ含む）
- ウェブトゥーン（韓国発・グローバル展開）
- アニメ（国内外）

調査言語：日本語・英語・中国語のニュース・SNS・レポート

以下の構成でHTMLレポートを作成してください：

1. 📰 ニュースサマリー（5〜8件、各言語から）
   - 日本語ニュース
   - 英語ニュース
   - 中国語・その他

2. 💬 SNS・ネット反響まとめ
   - Reddit（英語圏の反応）
   - LinkedIn（業界関係者の動向）
   - その他注目コメント

3. 🔮 未来への影響シナリオ分析（4つのシナリオ）
   - シナリオA：楽観シナリオ
   - シナリオB：現実的シナリオ
   - シナリオC：悲観シナリオ
   - シナリオD：ワイルドカード（予想外の展開）

4. 📚 深掘りするための推薦情報源
   - 今週読むべき記事・レポート3〜5件（URLつき）

HTMLは読みやすく、モバイルでも見やすいデザインにしてください。
背景色は白、アクセントカラーは #4A90E2（青）を使用。フォントはメイリオ・sans-serif。"""


def generate_report():
    """Claude APIを使ってレポートを生成（Web検索付き）"""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    print("🔍 レポートを生成中...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": USER_PROMPT}],
    )

    # テキストブロックを結合
    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    return html_content


def wrap_in_email_template(body_html, today):
    """メール用HTMLテンプレートでラップ"""
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>業界レポート {today}</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:'Meiryo',sans-serif;">
<div style="max-width:700px;margin:20px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

  <!-- ヘッダー -->
  <div style="background:#4A90E2;padding:24px 32px;">
    <h1 style="margin:0;color:#fff;font-size:20px;">📊 コミック・ウェブトゥーン・アニメ業界レポート</h1>
    <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">{today} | Powered by Claude</p>
  </div>

  <!-- 本文 -->
  <div style="padding:24px 32px;">
    {body_html}
  </div>

  <!-- フッター -->
  <div style="background:#f9f9f9;padding:16px 32px;border-top:1px solid #eee;">
    <p style="margin:0;color:#999;font-size:12px;">このレポートはClaude AIが自動生成しています。情報の正確性は各ソースでご確認ください。</p>
  </div>

</div>
</body>
</html>"""


def send_gmail(html_content, today):
    """GmailでHTMLメールを送信"""
    sender = os.environ["GMAIL_ADDRESS"]
    recipient = os.environ["REPORT_RECIPIENT_EMAIL"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📊 業界レポート {today}"
    msg["From"] = sender
    msg["To"] = recipient

    full_html = wrap_in_email_template(html_content, today)
    msg.attach(MIMEText(full_html, "html", "utf-8"))

    print("📧 メール送信中...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, app_password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"✅ 送信完了 → {recipient}")


def main():
    print(f"🚀 レポート生成開始: {today}")
    html_report = generate_report()
    send_gmail(html_report, today)
    print("🎉 完了！")


if __name__ == "__main__":
    main()
