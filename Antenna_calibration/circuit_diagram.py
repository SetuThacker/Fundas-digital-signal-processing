import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, RegularPolygon
import matplotlib.patheffects as PathEffects
from pathlib import Path

# Directory where this script is located
script_dir = Path(__file__).resolve().parent

# ==========================================
# 1. SETUP FIGURE AND STYLING
# ==========================================
fig, ax = plt.subplots(figsize=(24, 15), dpi=300, facecolor='#F8F9FA')
ax.set_xlim(0, 25)
ax.set_ylim(0, 16)
ax.axis('off')

# Color Palette for Paths
C_TX = "#D32F2F"   # Red (TXCAL)
C_RX = "#1976D2"   # Blue (RXCAL)
C_REF = "#388E3C"  # Green (REFCAL)
C_HW = "#FFFFFF"   # White hardware boxes
C_EDGE = "#212121" # Dark grey edges

title_font = {'fontsize': 14, 'fontweight': 'bold', 'color': 'black'}
label_font = {'fontsize': 11, 'fontweight': 'bold', 'ha': 'center', 'va': 'center'}

def add_box(x, y, w, h, text, facecolor=C_HW, dashed=False, lw=1.5, text_y=None, fontsize=None):
    ls = '--' if dashed else '-'
    box = Rectangle((x, y), w, h, fill=True, facecolor=facecolor, edgecolor=C_EDGE, lw=lw, linestyle=ls, zorder=2)
    ax.add_patch(box)
    if text:
        ty = text_y if text_y is not None else y + h/2
        fs = fontsize if fontsize else label_font['fontsize']
        ax.text(x + w/2, ty, text, fontsize=fs, fontweight=label_font['fontweight'], 
                ha=label_font['ha'], va=label_font['va'], zorder=3)

def draw_path(points, color, label_text, label_pos, arrow_locs):
    """Draws orthogonal signal paths with glowing outlines and directional arrows."""
    x, y = zip(*points)
    line, = ax.plot(x, y, color=color, lw=3.5, zorder=4)
    line.set_path_effects([PathEffects.withStroke(linewidth=7, foreground='white')])
    
    # Add arrows
    for i in arrow_locs:
        if i < len(points) - 1:
            ax.annotate('', xy=points[i+1], xytext=points[i],
                        arrowprops=dict(arrowstyle="->", color=color, lw=2.5, mutation_scale=20), zorder=5)
            
    # Add Text Label with glow
    if label_text and label_pos:
        txt = ax.text(label_pos[0], label_pos[1], label_text, color=color, fontweight='bold', fontsize=11, zorder=6)
        txt.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='white')])

# ==========================================
# 2. DRAW HARDWARE BLOCKS (RF JARGON)
# ==========================================

# --- RF Electronics (RFE) Block ---
add_box(1, 1.5, 4.5, 10.5, "", dashed=True, facecolor='none', lw=2)
ax.text(3.25, 12.5, "RF Electronics (RFE) /\nCentral Electronics", **title_font, ha='center')

add_box(1.5, 8.5, 3.5, 2.0, "Exciter /\nUpconverter (Tx)")
add_box(1.5, 3.0, 3.5, 2.0, "Downconverter /\nADC (Rx)")

# --- Cable Distribution Network (Middle) ---
ax.text(9.5, 11.5, "Analog Routing Network\n(Corporate Feed & CalNet)", **title_font, ha='center')

add_box(7.0, 8.5, 6, 2.0, "Tx/Rx Corporate Feed\n(Manifold)", text_y=9.55) 
add_box(7.0, 5.5, 6, 2.0, "Reference Path\n(Fixed Attenuator)", text_y=6.0) 
add_box(7.0, 2.5, 6, 2.0, "Calibration Network\n(CNW)", text_y=3.4) 

# --- Transmit/Receive Module (TRM) ---
add_box(14.5, 1.5, 8.5, 10.5, "", dashed=True, facecolor='none', lw=2)
ax.text(18.75, 12.5, "Transmit / Receive Module\n(TRM)", **title_font, ha='center')

# --- Antenna Radiator ---
add_box(23.5, 3.0, 0.8, 8.0, "Radiator\nElement", fontsize=9)

# HPA (Tx Amp) - Triangle pointing Right
ax.add_patch(RegularPolygon((19.0, 9.5), 3, radius=0.8, orientation=-1.57, fill=True, facecolor=C_HW, edgecolor=C_EDGE, lw=1.5, zorder=3))
ax.text(19.0, 9.5, "HPA\n(Tx)", **label_font, zorder=4)

# LNA (Rx Amp) - Triangle pointing Left
ax.add_patch(RegularPolygon((19.0, 4.5), 3, radius=0.8, orientation=1.57, fill=True, facecolor=C_HW, edgecolor=C_EDGE, lw=1.5, zorder=3))
ax.text(19.0, 4.5, "LNA\n(Rx)", **label_font, zorder=4)

# Directional Coupler (Circle)
coupler = Circle((21.2, 7.0), 0.6, fill=True, facecolor=C_HW, edgecolor=C_EDGE, lw=1.5, zorder=3)
ax.add_patch(coupler)
ax.plot([20.8, 21.6], [6.6, 7.4], color=C_EDGE, lw=1.5, zorder=4)
ax.text(21.2, 8.0, "Directional\nCoupler", fontsize=10, fontweight='bold', ha='center', zorder=4)

# --- Antenna Radiator ---
add_box(23.5, 3.0, 0.8, 8.0, "Radiator\nElement", label_font['fontsize'] - 2)
ax.plot([21.8, 23.5], [7.0, 7.0], color=C_EDGE, lw=2, zorder=1) 

# ==========================================
# 3. ROUTE SIGNAL PATHS (TXCAL, RXCAL, REFCAL)
# ==========================================

# --- Path 1: TXCAL (Red) ---
tx_points = [
    (5.0, 10.1), (7.0, 10.1), (13.0, 10.1), (14.0, 10.1), (14.0, 7.5), (15.5, 7.5), 
    (17.0, 7.5), (17.5, 7.5), (17.5, 9.5), (18.2, 9.5), 
    (19.8, 9.5), (21.2, 9.5), (21.2, 7.6), 
    (21.2, 6.4), (21.2, 3.9), (13.0, 3.9), 
    (7.0, 3.9), (6.0, 3.9), (6.0, 4.5), (5.0, 4.5)
]
draw_path(tx_points, C_TX, "TXCAL Tap ↓", (21.5, 5.2), arrow_locs=[1, 4, 8, 11, 15, 18])


# --- Path 2: RXCAL (Blue) ---
rx_points = [
    (5.0, 9.0), (5.8, 9.0), (5.8, 2.9), (7.0, 2.9), 
    (13.0, 2.9), (20.5, 2.9), (20.5, 6.8), (20.6, 6.8), 
    (20.6, 7.2), (20.0, 7.2), (20.0, 4.5), (19.8, 4.5), 
    (18.2, 4.5), (17.5, 4.5), (17.5, 6.5), (17.0, 6.5), 
    (15.5, 6.5), (14.5, 6.5), (14.5, 9.0), (13.0, 9.0), 
    (7.0, 9.0), (6.5, 9.0), (6.5, 3.5), (5.0, 3.5)
]
draw_path(rx_points, C_RX, "RXCAL Inject ↑", (19.2, 6.0), arrow_locs=[2, 4, 6, 10, 14, 18, 20, 22])


# --- Path 3: REFCAL (Green) ---
ref_points = [
    (5.0, 9.55), (6.2, 9.55), (6.2, 6.8), (7.0, 6.8), 
    (13.0, 6.8), (13.5, 6.8), (13.5, 4.0), (5.0, 4.0)
]
draw_path(ref_points, C_REF, "REFCAL Loop", (13.8, 5.5), arrow_locs=[2, 4, 6])


# ==========================================
# 4. LEGEND & ANNOTATIONS (TOP LEFT)
# ==========================================
add_box(0.5, 13.5, 7.2, 2.2, "", facecolor='white')
ax.text(4.1, 15.2, "Diagnostic Signal Paths", fontweight='bold', fontsize=12, ha='center')

ax.add_patch(FancyArrowPatch((0.8, 14.6), (2.3, 14.6), color=C_TX, lw=3, arrowstyle="->", mutation_scale=15, zorder=4))
ax.text(2.6, 14.6, "TXCAL (Measure Tx Chain / HPA)", fontweight='bold', va='center', fontsize=10, zorder=4)

ax.add_patch(FancyArrowPatch((0.8, 14.1), (2.3, 14.1), color=C_RX, lw=3, arrowstyle="->", mutation_scale=15, zorder=4))
ax.text(2.6, 14.1, "RXCAL (Measure Rx Chain / LNA)", fontweight='bold', va='center', fontsize=10, zorder=4)

ax.add_patch(FancyArrowPatch((0.8, 13.7), (2.3, 13.7), color=C_REF, lw=3, arrowstyle="->", mutation_scale=15, zorder=4))
ax.text(2.6, 13.7, "REFCAL (Measure System Drift)", fontweight='bold', va='center', fontsize=10, zorder=4)

# Save and Display
save_path = script_dir / "Custom_SAR_Cal_Architecture_RF_Accurate.png"
plt.savefig(save_path, bbox_inches='tight', dpi=300)
print(f"Publication diagram successfully saved to: {save_path}")

plt.show()