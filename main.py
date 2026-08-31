import os
import re
import requests
from bs4 import BeautifulSoup

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
TARGET_URL = "https://tryex.xyz/goya_scorechart.php?kind=NEARUSDT&hour=600"

def send_telegram_msg(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        response = requests.post(url, json=payload, timeout=10)
        res_json = response.json()
        if not res_json.get("ok"):
            print("텔레그램 전송 실패:", res_json)
    except Exception as e:
        print("네트워크 오류:", e)

def check_signal():
    try:
        response = requests.get("https://tryex.xyz/goya_list.php", timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text_data = soup.get_text()

            # Signal L1, L2, L3 및 S1, S2, S3 전체 탐색
            matches = re.findall(r'Signal (L[1-3]|S[1-3])\((\d+)H\)', text_data)

            for signal_type, hour_str in matches:
                hours_passed = int(hour_str)
                
                # 발생 1시간 이내(0H 또는 1H) 최신 신호만 감지
                if hours_passed <= 1:
                    msg = (
                        f"🚨 [고야 신규 신호 포착!]\n"
                        f"▪ 신호: {signal_type}\n"
                        f"▪ 경과: {hours_passed}시간 전\n"
                        f"🔗 차트: {TARGET_URL}"
                    )
                    send_telegram_msg(msg)
                    print(f"알림 전송 완료: Signal {signal_type}({hours_passed}H)")
                else:
                    print(f"오래된 신호 스킵: Signal {signal_type}({hours_passed}H)")
    except Exception as e:
        print("사이트 체크 중 오류:", e)

if __name__ == "__main__":
    check_signal()
