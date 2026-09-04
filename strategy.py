#!/usr/bin/env python3
"""蜂王震荡套利策略 —— 信号生成（一键跑）。
规律：冲高失败=阻力（涨到阻力做空）、探底失败=支撑（跌到支撑做多）。

跑法：
  python strategy.py                      # 自动：拉现价+读位，贴近阻力做空/贴近支撑做多，中间观望
  python strategy.py --direction short    # 强制发做空（测试/手动）
  python strategy.py --direction long     # 强制发做多
"""
import json, subprocess, urllib.request, gzip, io, argparse
from datetime import datetime, timezone
from pathlib import Path

STRATEGY_ID = "xrp_swing_v1"
SYMBOL = "XRP-USDT-SWAP"
QUANTITY = "10"
TP_PCT = 3.0    # 止盈 +3%
SL_PCT = 2.0    # 止损 -2%
TOUCH = 0.005   # 贴近 0.5% 触发
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ROOT = Path(__file__).resolve().parent


def get_last():
    """拉 XRP 现价（OKX 公共接口）。"""
    req = urllib.request.Request(f"https://www.okx.com/api/v5/market/ticker?instId={SYMBOL}",
                                 headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
    raw = urllib.request.urlopen(req, timeout=15).read()
    try:
        raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
    except Exception:
        pass
    return float(json.loads(raw.decode("utf-8", "replace"))["data"][0]["last"])


def load_levels():
    """读 level_coins.json 里 XRP 的阻力/支撑。"""
    p = ROOT.parent / "backtest" / "output" / "level_coins.json"
    if not p.exists():
        return None, None
    coins = json.loads(p.read_text(encoding="utf-8"))
    for c in coins:
        if c.get("base") == "XRP":
            return c.get("res"), c.get("sup")
    return None, None


def decide(last, res, sup):
    """0 观望 / -1 做空 / 1 做多。"""
    if res and last >= float(res) * (1 - TOUCH):
        return -1
    if sup and last <= float(sup) * (1 + TOUCH):
        return 1
    return 0


def emit_signal(direction, price):
    """写 latest.json + 归档 history + commit + push（触发机器人）。"""
    if direction == "short":
        stop_loss = round(price * (1 + SL_PCT / 100), 4)
        take_profit = round(price * (1 - TP_PCT / 100), 4)
    else:
        stop_loss = round(price * (1 - SL_PCT / 100), 4)
        take_profit = round(price * (1 + TP_PCT / 100), 4)

    signal = {
        "strategy_id": STRATEGY_ID, "symbol": SYMBOL, "direction": direction,
        "quantity": QUANTITY, "price": str(price), "stop_loss": str(stop_loss),
        "take_profit": str(take_profit), "confidence": 0.8,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open("signals/latest.json", "w", encoding="utf-8") as f:
        json.dump(signal, f, ensure_ascii=False, indent=2)
    date_str = signal["timestamp"][:10]
    with open(f"history/{date_str}.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(signal, ensure_ascii=False) + "\n")
    subprocess.run(["git", "add", "signals/latest.json", f"history/{date_str}.json"], check=True)
    subprocess.run(["git", "commit", "-m", f"signal: {direction} {SYMBOL} @ {price}"], check=True)
    subprocess.run(["git", "push"], check=True)
    print(f"[信号已推] {direction} {SYMBOL} @ {price} 止损{stop_loss} 止盈{take_profit}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--direction", choices=["short", "long"], help="强制指定方向（测试用）")
    args = ap.parse_args()

    res, sup = load_levels()
    last = get_last()
    print(f"XRP 现价 {last}  阻力 {res}  支撑 {sup}")

    if args.direction:
        emit_signal(args.direction, last)
    else:
        cur = decide(last, res, sup)
        if cur == 0:
            print("现价在中间，观望，不发信号")
        else:
            emit_signal("short" if cur == -1 else "long", last)
