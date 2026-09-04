#!/usr/bin/env python3
"""蜂王震荡套利策略 —— 信号生成。
规律：冲高失败=阻力（涨到阻力做空）、探底失败=支撑（跌到支撑做多）。
信号写入 signals/latest.json（9字段），git push 触发交易机器人。
止盈 +3%、止损 -2%。
"""
import json, subprocess
from datetime import datetime, timezone


def emit_signal(strategy_id, symbol, direction, quantity, price, stop_loss, take_profit, confidence):
    signal = {
        "strategy_id": strategy_id,
        "symbol": symbol,
        "direction": direction,
        "quantity": str(quantity),
        "price": str(price),
        "stop_loss": str(stop_loss),
        "take_profit": str(take_profit),
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # 写入最新信号
    with open("signals/latest.json", "w") as f:
        json.dump(signal, f, indent=2)

    # 归档到历史
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with open(f"history/{date_str}.json", "a") as f:
        f.write(json.dumps(signal) + "\n")

    # commit + push，触发我们的机器人
    subprocess.run(["git", "add", "signals/latest.json", f"history/{date_str}.json"])
    subprocess.run(["git", "commit", "-m", f"signal: {direction} {symbol} @ {price}"])
    subprocess.run(["git", "push"])
    print(f"[信号已推] {direction} {symbol} @ {price}")


if __name__ == "__main__":
    # 测试信号：XRP 做空（涨到阻力做空）
    emit_signal(
        strategy_id="xrp_swing_v1",
        symbol="XRP-USDT-SWAP",
        direction="short",
        quantity=10,
        price=1.4626,
        stop_loss=1.4919,
        take_profit=1.4187,
        confidence=0.8,
    )
