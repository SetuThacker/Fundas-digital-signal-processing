import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# ==========================================
# 1. Prepare Timeline Data 
# ==========================================
timeline_data = [
    {"Chunk": "1 (Tx Cal 56)", "Start": 0.0000, "Dur": 0.0301, "Phase": "Pre-amble", "Shape": "(50, 2454)", "Reason": "Measure transmit path characteristics"},
    {"Chunk": "2 (TxH Iso 56)", "Start": 0.0301, "Dur": 0.0301, "Phase": "Pre-amble", "Shape": "(50, 2454)", "Reason": "Isolate Tx hardware leakage"},
    {"Chunk": "3 (Rx Cal 6)", "Start": 0.0602, "Dur": 0.0301, "Phase": "Pre-amble", "Shape": "(50, 2454)", "Reason": "Measure receive path characteristics"},
    {"Chunk": "4 (EPDN 56)", "Start": 0.0903, "Dur": 0.0301, "Phase": "Pre-amble", "Shape": "(50, 2454)", "Reason": "Measure internal routing path"},
    {"Chunk": "5 (TA Cal 56)", "Start": 0.1204, "Dur": 0.0301, "Phase": "Pre-amble", "Shape": "(50, 2454)", "Reason": "Antenna array element monitoring"},
    {"Chunk": "6 (APDN 56)", "Start": 0.1505, "Dur": 0.0301, "Phase": "Pre-amble", "Shape": "(50, 2454)", "Reason": "Antenna path monitoring"},
    {"Chunk": "7-12 (Swath 92/42)", "Start": 0.1806, "Dur": 0.0599, "Phase": "Pre-amble", "Shape": "Various", "Reason": "Cross-swath calibration routing tests"},
    {"Chunk": "13 (Echo 6)", "Start": 0.2405, "Dur": 17.9948, "Phase": "Imaging", "Shape": "(29934, 19950)", "Reason": "Main Earth imaging observation"},
    {"Chunk": "14 (Echo 6)", "Start": 18.2353, "Dur": 11.9966, "Phase": "Imaging", "Shape": "(19956, 19986)", "Reason": "Main Earth imaging observation"},
    {"Chunk": "15-20 (Swath 92/42)", "Start": 30.2319, "Dur": 0.0599, "Phase": "Post-amble", "Shape": "Various", "Reason": "Cross-swath calibration routing tests"},
    {"Chunk": "21 (Tx Cal 56)", "Start": 30.2918, "Dur": 0.0301, "Phase": "Post-amble", "Shape": "(50, 2454)", "Reason": "Verify Tx path drift post-imaging"},
    {"Chunk": "22 (TxH Iso 56)", "Start": 30.3219, "Dur": 0.0301, "Phase": "Post-amble", "Shape": "(50, 2454)", "Reason": "Isolate Tx leakage post-imaging"},
    {"Chunk": "23 (Rx Cal 6)", "Start": 30.3520, "Dur": 0.0301, "Phase": "Post-amble", "Shape": "(50, 2454)", "Reason": "Verify Rx path drift post-imaging"},
    {"Chunk": "24 (EPDN 56)", "Start": 30.3821, "Dur": 0.0301, "Phase": "Post-amble", "Shape": "(50, 2454)", "Reason": "Verify EPDN path drift post-imaging"},
    {"Chunk": "25 (TA Cal 56)", "Start": 30.4122, "Dur": 0.0301, "Phase": "Post-amble", "Shape": "(50, 2454)", "Reason": "Verify antenna elements post-imaging"},
    {"Chunk": "26 (APDN 56)", "Start": 30.4423, "Dur": 0.0301, "Phase": "Post-amble", "Shape": "(50, 2454)", "Reason": "Verify antenna path post-imaging"}
]
df_time = pd.DataFrame(timeline_data)

max_end_time = (df_time["Start"].iloc[-1] + df_time["Dur"].iloc[-1]) + 2.0
color_map = {"Pre-amble": "#1f77b4", "Imaging": "#d62728", "Post-amble": "#2ca02c"}

# ==========================================
# 2. Prepare Block Diagram (Nodes)
# ==========================================
nodes = [
    dict(id="step1", text="<b>1. Filter Chunks</b><br>Target Swaths 56 & 6<br>(Pre & Post Amble)", x=0.5, y=0.95),
    dict(id="step2", text="<b>2. Leakage Suppression</b><br>Cal Chunks - TxH Iso<br><i>(Do NOT subtract from Echo)</i>", x=0.5, y=0.80),
    dict(id="step3", text="<b>3. Transient Cropping</b><br>Skip Initial 14 Pulses<br><i>(Bypass thermal warmup irregularities)</i>", x=0.5, y=0.65),
    dict(id="step4", text="<b>4. Signal Decoding</b><br>PCC-2 Subtraction<br>& Pulse Averaging", x=0.5, y=0.50),
    dict(id="step5", text="<b>5. PG Product</b><br>Master Replica = (Tx * Rx) / EPDN", x=0.5, y=0.35),
    dict(id="step6", text="<b>6A. Time Domain</b><br>Generate Hardware Chirp<br>(IFFT)", x=0.25, y=0.15),
    dict(id="step7", text="<b>6B. Frequency Domain</b><br>Transfer Function<br>(Magnitude & Phase)", x=0.75, y=0.15),
]

# ==========================================
# 3. Initialize Figure with Subplots
# ==========================================
fig = make_subplots(
    rows=1, cols=2, 
    column_widths=[0.45, 0.55],
    subplot_titles=("Satellite Execution Timeline (Use Slider to Zoom)", "Hardware Replica Processing Pipeline"),
    specs=[[{"type": "xy"}, {"type": "scatter"}]]
)

# ==========================================
# 4. Build Timeline (Left Subplot)
# ==========================================
for phase in ["Pre-amble", "Imaging", "Post-amble"]:
    df_subset = df_time[df_time["Phase"] == phase]
    
    customdata = df_subset[["Shape", "Reason"]].values
    
    fig.add_trace(
        go.Bar(
            x=df_subset["Dur"], 
            y=df_subset["Chunk"], 
            base=df_subset["Start"],
            orientation='h',
            name=phase,
            marker_color=color_map[phase],
            marker_line_color="black", 
            marker_line_width=1.5,
            customdata=customdata,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Start Time: %{base:.4f}s<br>"
                "Duration: %{x:.4f}s<br>"
                "Data Shape: %{customdata[0]}<br>"
                "Purpose: %{customdata[1]}"
                "<extra></extra>"
            )
        ),
        row=1, col=1
    )

fig.update_xaxes(
    title_text="Cumulative Time (s)", 
    type="linear", 
    range=[-0.5, max_end_time], 
    rangeslider=dict(
        visible=True, 
        thickness=0.08, 
        bgcolor="#f0f0f0",
        range=[-0.5, max_end_time] 
    ),
    row=1, col=1
)
fig.update_yaxes(
    title_text="Sequence Chunks", 
    autorange="reversed",
    fixedrange=True,
    row=1, col=1
)

# ==========================================
# 5. Build Flowchart (Right Subplot)
# ==========================================
fig.add_trace(
    go.Scatter(
        x=[n["x"] for n in nodes], 
        y=[n["y"] for n in nodes], 
        mode="markers", 
        marker=dict(size=1, color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="none"
    ),
    row=1, col=2
)

for node in nodes:
    fig.add_annotation(
        x=node["x"], y=node["y"],
        text=node["text"],
        showarrow=False,
        font=dict(size=13, color="black"),
        bgcolor="#e5ecf6",
        bordercolor="#2b3e50",
        borderwidth=2,
        borderpad=10,
        width=250, 
        row=1, col=2
    )

edges = [
    (0.5, 0.90, 0.5, 0.85),
    (0.5, 0.75, 0.5, 0.70),
    (0.5, 0.60, 0.5, 0.55),
    (0.5, 0.45, 0.5, 0.40),
    (0.5, 0.30, 0.25, 0.20),
    (0.5, 0.30, 0.75, 0.20),
]

for edge in edges:
    fig.add_annotation(
        x=edge[2], y=edge[3], 
        ax=edge[0], ay=edge[1], 
        xref="x2", yref="y2", axref="x2", ayref="y2",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor="#2b3e50",
        row=1, col=2
    )

# ADDED: fixedrange=True completely disables zoom/pan on the flowchart side
fig.update_xaxes(visible=False, range=[0, 1], fixedrange=True, row=1, col=2)
fig.update_yaxes(visible=False, range=[0, 1], fixedrange=True, row=1, col=2)

# ==========================================
# 6. Global Layout and Export
# ==========================================
fig.update_layout(
    title_text="<b>Sentinel-1 Acquisition & Processing Architecture</b>",
    title_x=0.5,
    font=dict(family="Arial, sans-serif"),
    height=800,
    width=1400,
    template="plotly_white",
    hovermode="closest",
    dragmode="zoom",
    showlegend=False  # ADDED: Removes the extreme right legend menu entirely
)

out_file = "sentinel1_pipeline_dashboard.html"
fig.write_html(out_file)
print(f"Successfully generated Plotly dashboard: {out_file}")