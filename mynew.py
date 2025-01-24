import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 解析 Query String 獲取資料
query_params = st.query_params
raw_data = query_params.get("data", [None])

if not raw_data:
    st.error("No data provided in the query parameters.")
    st.stop()

# 將資料轉換為 DataFrame
print(raw_data)
data = []
for item in raw_data.split(';'):
    rank, name, score = item.split(',')
    data.append({
        "rank": int(rank),
        "name": name,
        "score": int(score)
    })

df = pd.DataFrame(data)

# Reverse rank to flip the x-axis order
df["rank_reversed"] = max(df["rank"]) - df["rank"] + 1
df["x_position"] = max(df["rank"]) - df["rank"]

# Calculate differences between scores and their midpoints
df["score_diff"] = df["score"].diff(periods=-1).fillna(0).astype(int)  # Difference between consecutive scores
df["mid_x"] = (df["x_position"] + df["x_position"].shift(-1)) / 2  # Midpoint of x_position
df["mid_y"] = (df["score"] + df["score"].shift(-1)) / 2  # Midpoint of scores
df["score_diff_text"] = df["score_diff"].apply(lambda x: f"{abs(x)}" if x != 0 else "")
df["text_annotation"] = df["name"] + "<br>" + df["score"].astype(str)

# Define custom color mapping
color_map = {
    "tournament": "green",
    "keep": "blue",
    "demotion": "red"
}

# Assign dummy results for demo purposes (replace with actual logic)
df["result"] = ["tournament" if rank <= 4+4 else "keep" if rank <= 8+8 else "demotion" for rank in df["rank"]]

# Create the figure
fig = go.Figure()

# Add bars for each rank
for i, row in df.iterrows():
    fig.add_trace(go.Bar(
        x=[row["x_position"]],
        y=[row["score"]],
        marker_color=color_map[row["result"]],
        name=row["result"] if i == 0 else None,  # Show legend only once
        text=row["text_annotation"],
        textposition="outside",
        hoverinfo="text"
    ))

# Add line plot connecting the top of each bar
fig.add_trace(go.Scatter(
    x=df["x_position"],
    y=df["score"],
    mode="lines",
    line=dict(color="black", width=2),
    name="Score Line"
))

# Add text annotations for score differences
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df["mid_x"].iloc[i]],
        y=[df["mid_y"].iloc[i]],
        mode="text",
        text=[df["score_diff_text"].iloc[i]],
        textfont=dict(size=12, color="red"),
        showlegend=False
    ))

# Update layout
fig.update_layout(
    title="Duolingo League Bar Chart with Score Differences",
    xaxis=dict(
        tickmode="array",
        tickvals=df["x_position"],
        ticktext=df["rank"],
        title="Rank"
    ),
    yaxis=dict(title="Score"),
    barmode="group",
    height=700,
    width=1000,
    margin=dict(l=40, r=40, t=40, b=40)
)

# Display the plot
st.title("Duolingo League Visualization")
st.plotly_chart(fig)

# Show raw data as a table
st.subheader("Raw Data")
st.dataframe(df)