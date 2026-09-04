# 交易执行接口对接文档

蜂王策略出信号后，调用本接口自动下单。我们只负责执行，策略决策在你那边。

## 接口信息

- **服务地址**: `http://154.64.254.42:3001`
- **鉴权方式**: 请求头 `x-api-token: bee-exec-2024-secret`
- **数据格式**: JSON

## 接口列表

### 1. 下单

```
POST /api/exec/order
```

**请求参数**:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| instId | string | 是 | 交易对，如 `XRP-USDT-SWAP` |
| direction | string | 是 | `long` 做多 / `short` 做空 |
| quantity | number | 是 | 张数（XRP 1张=100币） |
| stop_loss | number | 否 | 止损价 |
| take_profit | number | 否 | 止盈价 |
| leverage | number | 否 | 杠杆，默认5 |

**请求示例**:

```bash
curl -X POST http://154.64.254.42:3001/api/exec/order \
  -H "x-api-token: bee-exec-2024-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "instId": "XRP-USDT-SWAP",
    "direction": "short",
    "quantity": 1,
    "stop_loss": 1.4919,
    "take_profit": 1.4187,
    "leverage": 5
  }'
```

**返回示例**:

```json
{
  "success": true,
  "data": {
    "order": [{"ordId": "xxx", "sCode": "0"}],
    "oco": [{"algoId": "xxx"}]
  }
}
```

### 2. 平仓

```
POST /api/exec/close
```

**请求参数**:

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| instId | string | 是 | 交易对 |
| quantity | number | 否 | 平仓张数，不传则全平 |

### 3. 查持仓

```
GET /api/exec/position?instId=XRP-USDT-SWAP
```

不传 instId 则返回所有合约持仓。

### 4. 查余额

```
GET /api/exec/balance
```

### 5. 健康检查

```
GET /api/exec/ping
```

## Python 调用示例

```python
import requests

EXEC_URL = "http://154.64.254.42:3001"
TOKEN = "bee-exec-2024-secret"
HEADERS = {"x-api-token": TOKEN, "Content-Type": "application/json"}

def place_order(instId, direction, quantity, stop_loss=None, take_profit=None, leverage=5):
    payload = {
        "instId": instId,
        "direction": direction,
        "quantity": quantity,
        "leverage": leverage
    }
    if stop_loss:
        payload["stop_loss"] = stop_loss
    if take_profit:
        payload["take_profit"] = take_profit
    r = requests.post(f"{EXEC_URL}/api/exec/order", json=payload, headers=HEADERS)
    return r.json()

def close_position(instId, quantity=None):
    payload = {"instId": instId}
    if quantity:
        payload["quantity"] = quantity
    r = requests.post(f"{EXEC_URL}/api/exec/close", json=payload, headers=HEADERS)
    return r.json()

def get_position(instId=None):
    params = {"instId": instId} if instId else {}
    r = requests.get(f"{EXEC_URL}/api/exec/position", params=params, headers=HEADERS)
    return r.json()

# 示例：做空1张XRP
result = place_order("XRP-USDT-SWAP", "short", 1, stop_loss=1.4919, take_profit=1.4187)
print(result)
```

## 注意事项

1. 下单为市价单，成交后自动设置 OCO 止盈止损
2. 逐仓模式，杠杆默认 5x
3. XRP 合约面值 100 币/张，下单前确认保证金充足
4. 接口有问题联系 H
