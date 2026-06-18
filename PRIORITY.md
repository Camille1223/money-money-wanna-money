# 📐 Priority Score · 优先级评分

> **🌐 Language:** [English](#-english) · [中文](#-中文)

---

## 🇬🇧 English

### The formula

```
Priority = Open EUR × (1 + OD days / 30)
```

Where `OD days` is the **maximum overdue-day count** across that customer's open invoices.

### What each factor means

- **`Open EUR`** — total EUR of all unpaid invoices for this customer. **Bigger amounts get higher weight** — recovering €1M and recovering €10k are not the same problem.
- **`(1 + OD days / 30)`** — overdue-severity multiplier:

  | OD days | Multiplier |
  |---:|---:|
  | 0 (not yet overdue) | 1.00 |
  | 30 (one month late) | 2.00 |
  | 60 (two months late) | 3.00 |
  | 90 (three months late) | 4.00 |

### Why it's designed this way

1. **`+1` instead of `+0`** — even when OD = 0, a freshly-billed large customer still deserves a base priority. Multiplying by zero would erase them entirely.
2. **Divide by 30 (monthly granularity)** — collectors instinctively bucket overdue into "30 / 60 / 90 days." Doubling the weight every month mirrors the urgency cadence of real outreach.
3. **Multiplication, not addition** — amount is the chassis, overdue is the magnifier. €50k × 90 days late = 50000 × 4 = 200,000; €500k × 0 days = 500,000 × 1 = 500,000. Better to chase the big fresh invoice than spend a week on a small old one.

### Example

| Customer | Open EUR | Max OD | Priority |
|---|---:|---:|---:|
| A | 100,000 | 0 d | 100,000 |
| B | 100,000 | 30 d | 200,000 |
| C | 100,000 | 90 d | **400,000** |
| D |  50,000 | 120 d | 250,000 |

The implicit question this ranking answers: **"Whom should I call first today?"**
C tops the list (big + severely overdue); D ranks second (half the amount but 5× the OD multiplier).

### This is a heuristic, not an accounting standard

Many collector tools use some variant of `amount × time`. If you want to:

- **Punish overdue more aggressively** → `Open EUR × (1 + OD/30)²` (quadratic)
- **Treat non-overdue as zero priority** → `Open EUR × OD/30` (drops the `+1`)
- **Softer overdue weight** → `Open EUR × (1 + OD/60)` (half-month buckets)

Tweak `index.html` — the formula is in one place, easy to edit.

---

## 🇨🇳 中文

### 公式

```
Priority = Open EUR × (1 + OD天数 / 30)
```

其中 `OD天数` 是**该客户所有未付单据中最大的逾期天数**。

### 两个因子的含义

- **`Open EUR`** —— 该客户所有未付单据的欧元合计。**金额越大权重越高**，因为追回 100 万和追回 1 万对回款率的影响完全不同。
- **`(1 + OD天数 / 30)`** —— 逾期严重度系数：

  | OD 天数 | 系数 |
  |---:|---:|
  | 0（还没逾期） | 1.00 |
  | 30（逾期一个月） | 2.00 |
  | 60（逾期两个月） | 3.00 |
  | 90（逾期三个月） | 4.00 |

### 为什么这么设计

1. **`+1` 不是 `+0`** —— 即使 OD = 0，刚开单的大额客户也得有基础优先级，不能直接 ×0 掉。
2. **除以 30 是月度颗粒度** —— AR 行业里对 OD 的直觉分档基本是「30/60/90」，每多一个月翻一倍权重，符合 collector 实际打电话的紧迫感节奏。
3. **乘法不是加法** —— 金额是底盘，逾期是放大镜。5 万 EUR × 90 天逾期 = 50000 × 4 = 200,000；50 万 EUR × 0 天 = 500,000 × 1 = 500,000。宁可先追大单再多催几次没逾期的，也比花一周追一笔小逾期划算。

### 举例对比

| 客户 | Open EUR | Max OD | Priority |
|---|---:|---:|---:|
| A | 100,000 | 0 d | 100,000 |
| B | 100,000 | 30 d | 200,000 |
| C | 100,000 | 90 d | **400,000** |
| D |  50,000 | 120 d | 250,000 |

这套排序的潜台词是：**"你今天该先打谁的电话？"**
C 排第一（金额大 + 严重逾期），D 第二（虽然金额一半但逾期翻 5 倍）。

### 这是经验型启发式公式，不是会计准则

行业里很多 collector 工具都是 `amount × time` 的变体。如果你想：

- **更激进地惩罚逾期** → `Open EUR × (1 + OD/30)²`（二次方）
- **没逾期的客户优先级归零** → `Open EUR × OD/30`（去掉 `+1`）
- **逾期权重温和一点** → `Open EUR × (1 + OD/60)`（半月一档）

改 `index.html`，公式只在一个地方，改起来很快。

---

<div align="center">

**[← Back to README](./README.md)** · **[← 返回主页](./README.md)**

</div>
