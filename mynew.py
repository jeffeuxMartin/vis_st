import datetime
import pytz
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 解析 Query String 獲取資料
query_params = st.query_params
tier_top = int(query_params.get("split1", "3"))
tier_bottom = int(query_params.get("split2", "10"))
MY_NAME = query_params.get("name", "Kaede かえで كايدي")

raw_data = query_params.get("data", [None])

if not raw_data:
    st.error("No data provided in the query parameters.")
    st.stop()

# 將資料轉換為 DataFrame
data = []
for item in raw_data.split(';'):
    rank, name, score = item.split(',')
    data.append({
        "rank": int(rank),
        "name": name,
        "score": int(score)
    })

df = pd.DataFrame(data)

Visualization_scale = df["score"].max()

# === 橫向佈局的座標 ===
# 以「排名 1 在最上方」為目標，使用連續的 y 位置
# 也可直接用 rank 當 y，然後 y 軸 reversed
df["y_position"] = df["rank"]  # 直接用 rank；等會用 yaxis.autorange="reversed"

# 分數差與註記位置（橫向版）
df["score_diff"] = df["score"].diff(periods=-1).fillna(0).astype(int)  # 下一名的差
df["mid_y"] = (df["y_position"] + df["y_position"].shift(-1)) / 2      # 兩名之間的 y 中點
df["mid_x"] = (df["score"] + df["score"].shift(-1)) / 2 + Visualization_scale * 0.12  # x 往右偏一點
df["score_diff_text"] = df["score_diff"].apply(lambda x: f"{abs(x)}" if x != 0 else "")
df["text_annotation"] = df["name"]

# 橫向版的分數數值標示位置：同一 y，上方改為右側位移
df["score_text_position_x"] = df["score"].apply(
    lambda x: (x + Visualization_scale * 0.03
               if x > Visualization_scale * 0.02 else
               x + Visualization_scale * 0.08)
)

# 顏色
color_map = {
    "tournament": "cyan",
    "keep": "blue",
    "demotion": "red"
}

def color_my_ify(color, is_me):
    if not is_me:
        return color
    if color == "cyan":
        return "rgba(0, 255, 0, 0.5)"
    elif color == "blue":
        return "rgba(100, 100, 255, 0.5)"
    elif color == "red":
        return "rgba(255, 100, 0, 0.5)"
    else:
        return "rgba(128, 128, 128, 0.5)"

# tier 決策
df["result"] = [
    "tournament" if rank <= tier_top else
    "keep" if rank <= tier_bottom else
    "demotion"
    for rank in df["rank"]
]

def color_determiner(row):
    return color_my_ify(
        color_map[row["result"]],
        is_me=(row["name"] == MY_NAME)
    )

def color_determiner2(row):
    c = color_determiner(row)
    if c == "rgba(0, 255, 0, 0.5)":
        return "green"
    elif c == "rgba(100, 100, 255, 0.5)":
        return "blue"
    elif c == "rgba(255, 100, 0, 0.5)":
        return "white"
    elif c == "rgba(128, 128, 128, 0.5)":
        return "gray"
    elif c == "cyan":
        return "black"
    elif c == "blue":
        return "yellow"
    elif c == "red":
        return "black"
    else:
        return "yellow"

# Figure
fig = go.Figure()

# 橫向長條
for i, row in df.iterrows():
    fig.add_trace(go.Bar(
        y=[row["y_position"]],
        x=[row["score"]],
        orientation="h",
        marker_color=color_determiner(row),
        text=(
            f'<a href='
            "https://www.example.com/"
            f' target="_blank">'
            f'<span style="color: {color_determiner2(row)};">'
            f'{row["text_annotation"]}'
            '</span>'
            '</a>'
        ),
        textfont=dict(
            size=14,
            color=("magenta" if row["name"] == MY_NAME
                   else "black" if row["result"] != "keep"
                   else "yellow"),
        ),
        showlegend=False,
        width=0.9,
        offsetgroup=0,
        base=0,
        hovertemplate=None,
    ))

# 連線（分數端點的折線，橫向）
fig.add_trace(go.Scatter(
    x=df["score"],
    y=df["y_position"],
    mode="lines",
    line=dict(color="black", width=2),
    name="Score Line",
    showlegend=False,
))

# 分數數值（顯示在條右側）
for i, row in df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["score_text_position_x"]],
        y=[row["y_position"]],
        mode="text",
        text=[row["score"]],
        textfont=dict(size=12, color="black"),
        showlegend=False
    ))

# 相鄰差值（放在兩名之間，x 往右偏）
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df["mid_x"].iloc[i]],
        y=[df["mid_y"].iloc[i]],
        mode="text",
        text=[df["score_diff_text"].iloc[i]],
        textfont=dict(size=16, color="magenta", weight="bold"),
        showlegend=False
    ))

# Layout（橫向）
fig.update_layout(
    xaxis=dict(title="Score"),
    yaxis=dict(
        tickmode="array",
        tickvals=df["y_position"],
        ticktext=df["rank"],
        title="Rank",
        autorange="reversed"  # 讓 rank=1 在上方
    ),
    barmode="group",
    margin=dict(r=40, t=30, b=10, pad=0),
)

# ===== START ===== #
# 🔹自動依 Score 軸刻度加上垂直線
xaxis_vals = fig.layout.xaxis.tickvals
if xaxis_vals:
    for x in xaxis_vals:
        fig.add_vline(x=x, line=dict(color="lightgray", width=1, dash="dot"), opacity=0.6)
else:
    fig.update_xaxes(showgrid=True, gridcolor="lightgray", gridwidth=1)
# -----  END  ----- #

# 關閉 hover
fig.update_traces(hoverinfo="none")

# 標題時間
formatted_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y/%m/%d %H:%M:%S')
fig.update_layout(title=f"{formatted_time}")

st.plotly_chart(fig)
