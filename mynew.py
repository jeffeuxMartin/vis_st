import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 解析 Query String 獲取資料
query_params = st.query_params
raw_data2 = query_params.get("split1", "8")
raw_data3 = query_params.get("split2", "16")
raw_data2 = eval(raw_data2)
raw_data3 = eval(raw_data3)

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
df["mid_y"] = ((df["score"] + df["score"].shift(-1)) / 2) * 1.05 # Midpoint of scores
df["score_diff_text"] = df["score_diff"].apply(lambda x: f"{abs(x)}" if x != 0 else "")
df["text_annotation"] = df["name"] + "<br />" + df["score"].astype(str)

# Define custom color mapping
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
        return "rgba(255, 0, 0, 0.5)"
    else:
        return "rgba(128, 128, 128, 0.5)"

# Assign dummy results for demo purposes (replace with actual logic)
df["result"] = [
    "tournament" if rank <= raw_data2 else 
    "keep" if rank <= raw_data3 else 
    "demotion" 
    for rank in df["rank"]]

# Create the figure
fig = go.Figure()


MY_NAME = "Kaede かえで كايدي"

# Add bars for each rank
for i, row in df.iterrows():
    fig.add_trace(go.Bar(
        x=[row["x_position"]],
        y=[row["score"]],
        marker_color=(
            color_my_ify(
                color_map[row["result"]],
                is_me=(row["name"] == MY_NAME)  # Replace with actual logic to check if it's the user's name
            )
        ),
        # name=row["result"] if i == 0 else None,  # Show legend only once
        text=row["text_annotation"],
        # textposition="outside",
        # hoverinfo="text"
        # hovertemplate=row["text_annotation"],
        textfont=dict(
            size=14, 
            # color="black",
            color=("magenta" if row["name"] == MY_NAME 
            else "black" if row["result"] != "keep"
            else "yellow"),
            # rotation=0,  # Rotate text to horizontal

        ),
        showlegend=False,
        width=0.9,  # Adjust bar width
        offsetgroup=0,  # Group bars together
        base=0,  # Set the base of the bar to 0
        # hovertemplate=row["text_annotation"],
        # hoverinfo="text",
        # hoverlabel=dict(bgcolor="white", font_size=16, font_family="Arial"),
        # hovertemplate="<b>%{text}</b><extra></extra>",
        # texttemplate="%{text}",
        # rotation=0,  # Rotate text to horizontal
        # turn_off_hover=True,
        # hovertemplate=(
            # "<b>%{text}</b><br>" +
            # "Rank: %{x}<br>" +
            # "Score: %{y}<extra></extra>"
        # ),
        hovertemplate=None,
        # texttemplate="%{text}",

    ))

# Add line plot connecting the top of each bar
fig.add_trace(go.Scatter(
    x=df["x_position"],
    y=df["score"],
    mode="lines",
    line=dict(color="black", width=2),
    name="Score Line",
    showlegend=False,
))

# Add text annotations for score differences
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df["mid_x"].iloc[i]],
        y=[df["mid_y"].iloc[i]],
        mode="text",
        text=[df["score_diff_text"].iloc[i]],
        textfont=dict(size=16, color="red",
                      # bold
                        # family="Arial",
                        weight="bold",
                      ),
        showlegend=False
    ))

# Update layout
fig.update_layout(
    # title="Duolingo League Bar Chart with Score Differences",
    xaxis=dict(
        tickmode="array",
        tickvals=df["x_position"],
        ticktext=df["rank"],
        title="Rank"
    ),
    yaxis=dict(title="Score"),
    barmode="group",
    height=600,
    # width=1000,
    margin=dict(
        # l=40,
        r=40,
        t=20,
        b=0,
        pad=0,
        )
       
)

# 居然要這樣才能讓 hovertemplate 不顯示！
fig.update_traces(
    hoverinfo="none",
    # hovertemplate="%{text}",
    # texttemplate="%{text}",
)

# Display the plot
st.title("Duolingo League Visualization")
st.plotly_chart(fig)

### # Show raw data as a table
### st.subheader("Raw Data")
### st.dataframe(df)
### 