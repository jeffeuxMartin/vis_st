# https://chatgpt.com/c/67f0295d-6414-800c-86f7-a7214afa4788


# http://localhost:8501/?split1=3&split2=10&data=1,Zeynep%20DURU%20YILDIRIM,47025;2,Tsuyo%20Naka,46805;3,Fumi,39351;4,m-koba,19303;5,Mila%20%E2%99%A1,15647;6,Kaede%20%E3%81%8B%E3%81%88%E3%81%A7%20%D9%83%D8%A7%D9%8A%D8%AF%D9%8A,15101;7,rocoreco,14071;8,Midoba,13483;9,%E3%83%9F%E3%82%AB,13443;10,%E3%83%9E%E3%82%B3,12449;11,AK%20verma,9224;12,%EA%B9%80%EC%A7%80%ED%9D%AC,7826;13,Neeraj%20Yadav,7099;14,Tatyana,722;15,Alex,309


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
df["rank_reversed"] = max(df["rank"]) - df["rank"] + 1
df["x_position"] = max(df["rank"]) - df["rank"]

df["score_diff"] = df["score"].diff(periods=-1).fillna(0).astype(int)
df["mid_x"] = (df["x_position"] + df["x_position"].shift(-1)) / 2
df["mid_y"] = (df["score"] + df["score"].shift(-1)) / 2

df["score_diff_text"] = df["score_diff"].apply(lambda x: f"{abs(x)}" if x != 0 else "")
df["text_annotation"] = df["name"]

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

df["result"] = [
    "tournament" if rank <= tier_top else 
    "keep" if rank <= tier_bottom else 
    "demotion" 
    for rank in df["rank"]
]

df = df.sort_values(by="score", ascending=False).reset_index(drop=True)

fig = go.Figure()

for i, row in df.iterrows():
    fig.add_trace(go.Bar(
        y=[row["rank"]],
        x=[row["score"]],
        orientation='h',
        marker_color=color_my_ify(color_map[row["result"]], row["name"] == MY_NAME),
        text=f"{row['name']} <br /> {row['score']}",  # 顯示名字和分數在長條上
        textposition='inside',  # 名字放在長條內部
        name=row["text_annotation"],
        showlegend=False,
    ))

fig.add_trace(go.Scatter(
    y=df["rank"],
    x=df["score"],
    mode="lines",
    line=dict(color="black", width=2),
    name="Score Line",
    showlegend=False,
))

# 標註分數差異
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df["mid_y"].iloc[i]],
        y=[(df["rank"].iloc[i] + df["rank"].iloc[i + 1]) / 2],
        mode="text",
        text=[df["score_diff_text"].iloc[i]],
        textfont=dict(size=14, color="magenta"),
        showlegend=False
    ))

fig.update_layout(
    yaxis=dict(
        title="Rank",
        autorange="reversed",  # 確保最高分在最上面
        tickmode="array",
        tickvals=df["rank"],
        ticktext=df["rank"],
    ),
    xaxis=dict(title="Score"),
    barmode="stack",
    margin=dict(l=40, r=40, t=40, b=40),
    height=800,
    title=f"Ranking Visualization - {datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y/%m/%d %H:%M:%S')}"
)

st.plotly_chart(fig)
