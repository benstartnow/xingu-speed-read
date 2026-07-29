#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新股速读生成器 v2：读 data.json -> 黑金风速读卡 HTML（截图风格）。

用法:
    python3 gen_xg.py data.json out.html
"""
import json
import sys
import os

CSS = r"""
:root{
  --bg:#0d0f14; --panel:#151921; --panel2:#0a0c11;
  --acc:#e8c87a; --acc2:#f5d896; --acc-dim:#7a6438;
  --txt:#e6e9ef; --sub:#9aa3b2;
  --up:#ff4d4f; --down:#52c41a; --warn:#faad14;
  --line:#262c38; --line2:#1a1f2a;
}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{background:var(--bg);}
body{
  color:var(--txt);
  font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;
  padding:32px 18px 60px; line-height:1.6;
  background:
    radial-gradient(900px 500px at 80% -10%, rgba(232,200,122,.08), transparent 60%),
    radial-gradient(700px 400px at 10% 110%, rgba(232,200,122,.05), transparent 60%),
    var(--bg);
}
.wrap{max-width:780px;margin:0 auto;}

/* 顶部标题区 */
.hero{
  display:grid; grid-template-columns:1fr auto; gap:18px;
  align-items:start; padding-bottom:18px;
  border-bottom:1px solid var(--line);
  margin-bottom:18px;
}
.hero .left{min-width:0;}
.kicker{
  display:inline-block; color:var(--acc);
  font-size:12px; letter-spacing:2px;
  border:1px solid var(--acc-dim); border-radius:20px;
  padding:3px 12px; margin-bottom:12px;
}
.hero h1{
  font-size:48px; font-weight:800;
  background:linear-gradient(180deg, #f5d896 0%, #c9a14a 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
  letter-spacing:2px; line-height:1.1;
  text-shadow:0 0 24px rgba(232,200,122,.15);
}
.code-row{color:var(--sub); font-size:14px; margin-top:8px;}
.code-row b{color:var(--txt); font-weight:600;}
.position{
  display:inline-block; margin-top:12px;
  border:1px solid var(--acc-dim); border-radius:8px;
  padding:6px 14px; color:var(--acc);
  font-size:13px; letter-spacing:1px;
  background:rgba(232,200,122,.04);
}
/* 右上角芯片装饰 */
.chip{
  width:120px; height:120px; position:relative;
  background:
    radial-gradient(circle at 35% 35%, #2a2418 0%, #0c0a08 60%, #050505 100%);
  border:1px solid var(--acc-dim);
  border-radius:14px;
  box-shadow:0 0 24px rgba(232,200,122,.15), inset 0 0 16px rgba(232,200,122,.08);
  display:flex; align-items:center; justify-content:center;
  overflow:hidden;
}
.chip::before{
  content:""; position:absolute; inset:6px;
  border:1px solid rgba(232,200,122,.18); border-radius:10px;
  background:
    repeating-linear-gradient(0deg, transparent 0 5px, rgba(232,200,122,.06) 5px 6px),
    repeating-linear-gradient(90deg, transparent 0 5px, rgba(232,200,122,.06) 5px 6px);
}
.chip::after{
  content:""; position:absolute;
  width:60%; height:60%; top:20%; left:20%;
  background:linear-gradient(135deg, #1a1408 0%, #0a0805 100%);
  border-radius:8px; border:1px solid rgba(232,200,122,.2);
}
.chip .brand{
  position:relative; z-index:2; color:var(--acc);
  font-weight:800; font-size:22px; letter-spacing:3px;
  text-shadow:0 0 12px rgba(232,200,122,.5);
}

/* 卡片 */
.card{
  background:linear-gradient(180deg, var(--panel) 0%, var(--panel2) 100%);
  border:1px solid var(--line);
  border-radius:14px;
  padding:18px 20px;
  margin-bottom:14px;
  position:relative;
  box-shadow:0 1px 0 rgba(232,200,122,.04) inset, 0 6px 20px rgba(0,0,0,.25);
}
.card h2{
  display:flex; align-items:center; gap:10px;
  font-size:16px; color:var(--acc);
  margin-bottom:14px; letter-spacing:1px; font-weight:600;
}
.card h2 .num{
  display:inline-flex; align-items:center; justify-content:center;
  width:22px; height:22px; border-radius:50%;
  background:rgba(232,200,122,.12); color:var(--acc);
  font-size:13px; font-weight:700;
}

/* 事实卡 */
.fact{display:grid; grid-template-columns:repeat(6,1fr); gap:10px;}
.fact .cell{
  background:rgba(0,0,0,.25);
  border:1px solid var(--line2);
  border-radius:10px;
  padding:12px 10px; text-align:center;
}
.fact .ic{font-size:18px; color:var(--acc); margin-bottom:6px;}
.fact .k{font-size:11px; color:var(--sub); margin-bottom:4px;}
.fact .v{font-size:18px; color:#fff; font-weight:700;}
.fact .v.up{color:var(--up);}
.fact .v small{font-size:11px; color:var(--sub); font-weight:400; display:block; margin-top:2px;}

/* 板块规则区分 */
.rules{display:grid; grid-template-columns:1fr 1fr; gap:20px; align-items:center;}
.rules .kline{background:rgba(0,0,0,.3); border:1px solid var(--line2); border-radius:10px; padding:10px;}
.rules ul{list-style:none; padding:0;}
.rules li{
  position:relative; padding-left:18px; margin:8px 0;
  font-size:13px; color:var(--txt);
}
.rules li::before{
  content:""; position:absolute; left:0; top:9px;
  width:6px; height:6px; border-radius:50%;
  background:var(--acc);
  box-shadow:0 0 6px var(--acc);
}

/* 产业链地图 */
.chain{display:grid; grid-template-columns:1fr 1.2fr 1fr; gap:14px; align-items:stretch;}
.chain .col{
  background:rgba(0,0,0,.3);
  border:1px solid var(--line2);
  border-radius:10px;
  padding:14px 12px;
  display:flex; flex-direction:column;
}
.chain .col.up{border-top:2px solid var(--down);}
.chain .col.mid{
  border:1px solid var(--acc-dim);
  background:radial-gradient(circle at 50% 50%, rgba(232,200,122,.08) 0%, rgba(0,0,0,.3) 70%);
  display:flex; align-items:center; justify-content:center;
  text-align:center; min-height:200px;
}
.chain .col.down{border-top:2px solid var(--sub);}
.chain .col h3{font-size:12px; color:var(--sub); margin-bottom:10px; letter-spacing:1px;}
.chain .col.up h3{color:var(--down);}
.chain .col.mid h3{color:var(--acc);}
.chain .items{display:flex; flex-direction:column; gap:8px; flex:1;}
.chain .it{
  display:flex; align-items:center; gap:8px;
  font-size:13px; color:var(--txt);
  padding:4px 6px; border-radius:6px;
}
.chain .it .ico{color:var(--acc); font-size:14px; width:18px; text-align:center;}
/* 中游芯片 */
.chip-mini{
  position:relative; width:120px; height:120px; margin:6px auto 8px;
  background:radial-gradient(circle at 35% 35%, #2a2418 0%, #0c0a08 60%, #050505 100%);
  border:1px solid var(--acc-dim);
  border-radius:12px;
  box-shadow:0 0 18px rgba(232,200,122,.2);
  display:flex; align-items:center; justify-content:center;
  overflow:hidden;
}
.chip-mini::before{
  content:""; position:absolute; inset:5px;
  border:1px solid rgba(232,200,122,.2); border-radius:8px;
  background:
    repeating-linear-gradient(0deg, transparent 0 4px, rgba(232,200,122,.07) 4px 5px),
    repeating-linear-gradient(90deg, transparent 0 4px, rgba(232,200,122,.07) 4px 5px);
}
.chip-mini::after{
  content:""; position:absolute; width:55%; height:55%; top:22%; left:22%;
  background:linear-gradient(135deg, #1a1408 0%, #0a0805 100%);
  border-radius:6px; border:1px solid rgba(232,200,122,.3);
}
.chip-mini .logo{position:relative; z-index:2; color:var(--acc); font-weight:800; font-size:18px; letter-spacing:2px; text-shadow:0 0 10px rgba(232,200,122,.6);}
.chain .mid-name{color:var(--acc); font-size:18px; font-weight:700; letter-spacing:2px; margin-top:2px;}
.chain .mid-sub{color:var(--sub); font-size:12px; margin-top:4px;}
/* 上下游箭头 */
.arrow{
  position:absolute; top:50%; transform:translateY(-50%);
  color:var(--acc); font-size:20px; opacity:.6;
  z-index:3;
}
.arrow.l{left:-10px;}
.arrow.r{right:-10px;}
.chain-wrap{position:relative;}

/* 可比公司表 */
table{width:100%; border-collapse:collapse;}
th,td{text-align:left; padding:10px 8px; font-size:13px; border-bottom:1px solid var(--line2);}
th{color:var(--acc); font-weight:600; font-size:12px; letter-spacing:1px;}
tr:last-child td{border-bottom:none;}
td .nm{color:var(--txt); font-weight:600; display:flex; align-items:center; gap:8px;}
td .nm::before{content:""; width:5px; height:5px; background:var(--acc); border-radius:50%; display:inline-block;}
td.note{color:var(--sub);}

/* 风险提示 */
.risk{display:flex; flex-direction:column; gap:10px;}
.risk li{
  display:flex; gap:10px; align-items:flex-start;
  background:rgba(250,173,20,.06);
  border:1px solid rgba(250,173,20,.18);
  border-radius:8px;
  padding:10px 12px;
  font-size:13px; color:var(--txt);
  list-style:none;
}
.risk li .ic{
  color:var(--warn); font-size:16px; flex-shrink:0; margin-top:1px;
}

/* 底部 */
.foot{
  margin-top:24px; padding-top:14px;
  border-top:1px solid var(--line);
  text-align:center;
  color:var(--sub); font-size:11px; letter-spacing:2px;
}
.foot .acc{color:var(--acc);}

@media (max-width:680px){
  .hero{grid-template-columns:1fr;}
  .chip{width:80px; height:80px; margin-top:8px;}
  .hero h1{font-size:36px;}
  .fact{grid-template-columns:repeat(3,1fr);}
  .chain{grid-template-columns:1fr;}
  .rules{grid-template-columns:1fr;}
}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>新股速读 · {stock}</title><style>{css}</style></head>
<body><div class="wrap">

<div class="hero">
  <div class="left">
    <div class="kicker">新股速读 · 工具生成</div>
    <h1>{stock}</h1>
    <div class="code-row"><b>{code}</b> · {board} · 上市 {list_date}</div>
    <div class="position">{position}</div>
  </div>
  <div class="chip"><span class="brand">{chip_logo}</span></div>
</div>

<div class="card">
  <h2><span class="num">1</span>事实卡</h2>
  <div class="fact">
    <div class="cell"><div class="ic">📅</div><div class="k">上市日</div><div class="v">{list_date}</div></div>
    <div class="cell"><div class="ic">¥</div><div class="k">发行价</div><div class="v">{issue_price}<small>元</small></div></div>
    <div class="cell"><div class="ic">📈</div><div class="k">首日收盘</div><div class="v up">{first_close}<small>+{first_change_pct}%</small></div></div>
    <div class="cell"><div class="ic">🏛</div><div class="k">市值</div><div class="v">{mktcap_yi}<small>亿</small></div></div>
    <div class="cell"><div class="ic">💰</div><div class="k">首日成交</div><div class="v">{turnover_yi}<small>亿</small></div></div>
    <div class="cell"><div class="ic">💼</div><div class="k">募资</div><div class="v">{raise_yi}<small>亿</small></div></div>
  </div>
</div>

<div class="card">
  <h2><span class="num">2</span>板块规则区分</h2>
  <div class="rules">
    <div class="kline">{kline_svg}</div>
    <ul>
      <li>科创板前 5 交易日不设涨跌幅</li>
      <li>涨跌达 30% / 60% 各停牌 10 分钟</li>
      <li>第 6 日起 ±20% 涨跌幅限制</li>
    </ul>
  </div>
</div>

<div class="card">
  <h2><span class="num">3</span>产业链地图</h2>
  <div class="chain-wrap">
    <span class="arrow l">◀</span>
    <span class="arrow r">▶</span>
    <div class="chain">
      <div class="col up">
        <h3>上游 · 设备材料供应商</h3>
        <div class="items">{chain_up}</div>
      </div>
      <div class="col mid">
        <div>
          <h3>中游 · 发行人自身</h3>
          <div class="chip-mini"><span class="logo">{chip_logo}</span></div>
          <div class="mid-name">{stock}</div>
          <div class="mid-sub">IDM 一体化</div>
        </div>
      </div>
      <div class="col down">
        <h3>下游 · 封装测试与模组厂</h3>
        <div class="items">{chain_down}</div>
      </div>
    </div>
  </div>
  <div style="margin-top:12px;color:var(--sub);font-size:12px;text-align:center;letter-spacing:1px;">上游为设备材料供应商，下游为封装测试与模组厂，中游为发行人自身（IDM 一体化）。</div>
</div>

<div class="card">
  <h2><span class="num">4</span>可比公司（客观定位，不打分）</h2>
  <table><tr><th>公司</th><th>定位</th></tr>{comparables}</table>
</div>

<div class="card">
  <h2><span class="num">5</span>中性风险提示</h2>
  <ul class="risk">{risks}</ul>
</div>

<div class="foot"><span class="acc">新股速读</span> · 中性事实型工具 · 不荐股不打分不预测涨跌</div>

</div></body></html>"""


# 简化 K 线（示意）：前5日震荡上行 + 第6日起进入 ±20% 区间
KLINE_SVG = """
<svg viewBox="0 0 280 120" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">
  <defs>
    <linearGradient id="kl" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e8c87a" stop-opacity=".5"/>
      <stop offset="1" stop-color="#e8c87a" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <!-- 网格 -->
  <line x1="0" y1="30" x2="280" y2="30" stroke="#1a1f2a" stroke-dasharray="3 3"/>
  <line x1="0" y1="60" x2="280" y2="60" stroke="#1a1f2a" stroke-dasharray="3 3"/>
  <line x1="0" y1="90" x2="280" y2="90" stroke="#1a1f2a" stroke-dasharray="3 3"/>
  <!-- 分隔线 -->
  <line x1="140" y1="6" x2="140" y2="114" stroke="#e8c87a" stroke-opacity=".35" stroke-dasharray="4 3"/>
  <text x="70" y="118" fill="#9aa3b2" font-size="9" text-anchor="middle">前 5 日</text>
  <text x="210" y="118" fill="#9aa3b2" font-size="9" text-anchor="middle">第 6 日起</text>
  <!-- 前5日 K 线 (快速冲高回落) -->
  <g stroke="#ff4d4f" stroke-width="1.4">
    <line x1="14" y1="92" x2="14" y2="58"/>
    <line x1="40" y1="74" x2="40" y2="40"/>
    <line x1="66" y1="56" x2="66" y2="22"/>
    <line x1="92" y1="40" x2="92" y2="14"/>
    <line x1="118" y1="28" x2="118" y2="50"/>
  </g>
  <line x1="6" y1="78" x2="132" y2="34" stroke="#e8c87a" stroke-width="1.2" stroke-opacity=".4"/>
  <!-- 第6日起 ±20% 通道 -->
  <g stroke="#52c41a" stroke-width="1.4">
    <line x1="148" y1="34" x2="148" y2="58"/>
    <line x1="174" y1="40" x2="174" y2="64"/>
    <line x1="200" y1="44" x2="200" y2="68"/>
    <line x1="226" y1="50" x2="226" y2="74"/>
    <line x1="252" y1="38" x2="252" y2="62"/>
    <line x1="278" y1="44" x2="278" y2="68"/>
  </g>
  <line x1="142" y1="28" x2="282" y2="28" stroke="#52c41a" stroke-opacity=".4" stroke-dasharray="3 2"/>
  <line x1="142" y1="80" x2="282" y2="80" stroke="#52c41a" stroke-opacity=".4" stroke-dasharray="3 2"/>
  <text x="142" y="22" fill="#9aa3b2" font-size="8">+20%</text>
  <text x="142" y="92" fill="#9aa3b2" font-size="8">-20%</text>
  <!-- 停牌标注 -->
  <g fill="#faad14" font-size="9" font-family="-apple-system,'PingFang SC',sans-serif">
    <text x="92" y="10" text-anchor="middle">+30%</text>
    <text x="92" y="22" text-anchor="middle" font-size="7.5" fill="#9aa3b2">停牌 10 分钟</text>
    <text x="118" y="6" text-anchor="middle">+60%</text>
    <text x="118" y="18" text-anchor="middle" font-size="7.5" fill="#9aa3b2">停牌 10 分钟</text>
  </g>
</svg>
"""


def render(d):
    up_items = "".join(
        f'<div class="it"><span class="ico">◆</span>{x}</div>' for x in d.get("chain_up", [])
    )
    down_items = "".join(
        f'<div class="it"><span class="ico">◆</span>{x}</div>' for x in d.get("chain_down", [])
    )
    comp = "".join(
        f'<tr><td><span class="nm">{c["name"]}</span></td><td class="note">{c["note"]}</td></tr>'
        for c in d.get("comparables", [])
    )
    risk = "".join(f'<li><span class="ic">⚠</span><span>{r}</span></li>' for r in d.get("risks", []))
    return TEMPLATE.format(
        css=CSS,
        stock=d["stock"],
        code=d["code"],
        board=d["board"],
        list_date=d["list_date"],
        position=d["position"],
        chip_logo=d.get("chip_logo", d["stock"][:2].upper()),
        issue_price=d["issue_price"],
        first_close=d["first_close"],
        first_change_pct=d["first_change_pct"],
        mktcap_yi=d["mktcap_yi"],
        turnover_yi=d["turnover_yi"],
        raise_yi=d["raise_yi"],
        kline_svg=KLINE_SVG,
        chain_up=up_items,
        chain_down=down_items,
        comparables=comp,
        risks=risk,
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    data_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "examples", "data.json")
    if not os.path.exists(data_path):
        data_path = os.path.join(os.getcwd(), "data.json")
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.getcwd(), "新股速读_out.html")
    d = json.load(open(data_path, encoding="utf-8"))
    open(out_path, "w", encoding="utf-8").write(render(d))
    print(f"✅ 新股速读已生成: {out_path}")


if __name__ == "__main__":
    main()
