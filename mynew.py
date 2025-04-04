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

Visualization_scale = (
    df["score"].max()
)
# st.write("Visualization_scale: ", Visualization_scale)
# Reverse rank to flip the x-axis order
df["rank_reversed"] = max(df["rank"]) - df["rank"] + 1
df["x_position"] = max(df["rank"]) - df["rank"]

# Calculate differences between scores and their midpoints
df["score_diff"] = df["score"].diff(periods=-1).fillna(0).astype(int)  # Difference between consecutive scores
df["mid_x"] = (df["x_position"] + df["x_position"].shift(-1)) / 2  # Midpoint of x_position
# df["mid_y"] = ((df["score"] + df["score"].shift(-1)) / 2) * 1.09 # Midpoint of scores
df["mid_y"] = (df["score"] + df["score"].shift(-1)) / 2 * 1 + Visualization_scale * 0.12 # Midpoint of scores
df["score_diff_text"] = df["score_diff"].apply(lambda x: f"{abs(x)}" if x != 0 else "")
# df["text_annotation"] = df["name"] + "<br />" + df["score"].astype(str)
df["text_annotation"] = df["name"]
df["score_text_position"] = df["score"].apply(
    lambda x: (x + Visualization_scale * 0.03 
               if x > Visualization_scale * 0.02 else
               x + Visualization_scale * 0.08)  # Adjust text position based on score
)


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
        return "rgba(255, 100, 0, 0.5)"
    else:
        return "rgba(128, 128, 128, 0.5)"

# Assign dummy results for demo purposes (replace with actual logic)
df["result"] = [
    "tournament" if rank <= tier_top else 
    "keep" if rank <= tier_bottom else 
    "demotion" 
    for rank in df["rank"]]


# Create the figure
fig = go.Figure()



def color_determiner(
        row,
):
    result = color_my_ify(
                color_map[row["result"]],
                is_me=(row["name"] == MY_NAME)  # Replace with actual logic to check if it's the user's name
            )
    return result

def color_determiner2(
        row,
):
    if color_determiner(row) == "rgba(0, 255, 0, 0.5)":
        return "green"
    elif color_determiner(row) == "rgba(100, 100, 255, 0.5)":
        return "blue"
    elif color_determiner(row) == "rgba(255, 100, 0, 0.5)":
        return "white"
    elif color_determiner(row) == "rgba(128, 128, 128, 0.5)":
        return "gray"
    elif color_determiner(row) == "cyan":
        return "black"
    elif color_determiner(row) == "blue":
        return "yellow"
    elif color_determiner(row) == "red":
        return "black"
    else:
        return "yellow"


# Add bars for each rank
for i, row in df.iterrows():
    fig.add_trace(go.Bar(
        x=[row["x_position"]],
        y=[row["score"]],
        marker_color=(
            color_determiner(row)
        ),
        # name=row["result"] if i == 0 else None,  # Show legend only once
        
        # text=row["text_annotation"],
        # === add url
        text=(
            f'<a href='
                "https://www.example.com/"
            f' target="_blank">'
            f'<span style="color: {color_determiner2(row)};">'
            f'{row["text_annotation"]}'
            '</span>'
            '</a>',
        ),
        textfont=dict(
            size=14, 
            # color="black",
            color=("magenta" if row["name"] == MY_NAME 
            else "black" if row["result"] != "keep"
            else "yellow"),
        ),
        showlegend=False,
        width=0.9,  # Adjust bar width
        offsetgroup=0,  # Group bars together
        base=0,  # Set the base of the bar to 0
        hovertemplate=None,
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

# Add text annotations for scores
for i, row in df.iterrows():
    fig.add_trace(go.Scatter(
        x=[row["x_position"]],
        y=[row["score_text_position"]],
        mode="text",
        text=[row["score"]],
        textfont=dict(size=12, color="black"),
        showlegend=False
    ))


# Add text annotations for score differences
for i in range(len(df) - 1):
    fig.add_trace(go.Scatter(
        x=[df["mid_x"].iloc[i]],
        y=[df["mid_y"].iloc[i]],
        mode="text",
        text=[df["score_diff_text"].iloc[i]],
        textfont=dict(size=16, color="magenta",
                      # bold
                        # family="Arial",
                        weight="bold",
                      ),
        showlegend=False
    ))

# Update layout
fig.update_layout(
    xaxis=dict(
        tickmode="array",
        tickvals=df["x_position"],
        ticktext=df["rank"],
        title="Rank"
    ),
    # horizonal

    yaxis=dict(title="Score"),
    barmode="group",
    # height=400,
    # width=1000,
    margin=dict(
        # l=40,
        r=40,
        t=30,
        b=10,
        pad=0,
        )
       
)



# 居然要這樣才能讓 hovertemplate 不顯示！
fig.update_traces(
    hoverinfo="none",
)

formatted_time = datetime.datetime.now(pytz.timezone('Asia/Taipei')).strftime('%Y/%m/%d %H:%M:%S')

# 創建 Plotly 
fig.update_layout(
    title="{}".format(formatted_time)
)


# Display the plot
# st.title("Duolingo League Visualization")
# st.title("排名")


# add a button to download the plot as png
# st.download_button(
#     label="Download Plot",
#     data=fig.to_image(format="png"),
#     file_name="plot.png",
#     mime="image/png",
# )

import io

# 將圖表轉換為 PNG 格式的二進制資料
# img_bytes = fig.to_image(format="png", engine="kaleido")
# 
# # 使用 io.BytesIO 將資料轉換成 stream
# buffer = io.BytesIO(img_bytes)

# # 添加下載按鈕
# st.download_button(
#     label="Download Plot",
#     data=buffer,
#     file_name="plot.png",
#     mime="image/png",
# )



st.plotly_chart(fig)

### # Show raw data as a table
### st.subheader("Raw Data")
### st.dataframe(df)
### 
