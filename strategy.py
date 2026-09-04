#!/usr/bin/env python3
"""蜂王震荡套利策略 —— 信号生成。
规律：冲高失败=阻力（涨到阻力做空）、探底失败=支撑（跌到支撑做多）。
信号写入 signals/latest.json（9字段），git push 触发交易机器人。
止盈 +3%、止损 -2%。
"""
import json, subprocess
from datetime import datetime, timezone

def emit_signal(strategy_id, symbol, direction, quantity, price, stop_loss, take_profit, confidence):
    signal = {"strategy_id": strategy_id, "symbol": symbol, "direction": direction,
              "quantity": str(quantity), "price": str(price), "stop_loss": str(stop_loss),
              "take_profit": str(take_profit), "confidence": confidence,
              "timestamp": datetime.now(timezone.utc).isoformat()}
    with open("signals/latest.json", "w", encoding="utf-8") as f:
        json.dump(signal, f, ensure_ascii=False, indent=2)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(f"history/{date_str}.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(signal) + "
")
    subprocess.run(["git", "add", "signals/latest.json", f"history/{date_str}.json"])
    subprocess.run(["git", "commit", "-m", f"signal: {direction} {symbol} @ {price}"])
    subprocess.run(["git", "push"])
    print(f"[信号已推] {direction} {symbol} @ {price}")
