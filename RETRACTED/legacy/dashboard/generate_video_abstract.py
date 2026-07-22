#!/usr/bin/env python3
"""Generate animated video abstract as GIF.
Shows the differential effect: format bias bars dropping, content bias bars rising.
"""
import numpy as np
from pathlib import Path

OUT = Path(__file__).parent.parent / "dashboard" / "video_abstract.gif"

print("="*60)
print("VIDEO ABSTRACT GENERATOR")
print("="*60)
print("""
The video abstract will show:

FRAME 1 (0-3s): Three bar pairs appear  Rubric Order, Score ID, Reference Answer
  Each pair shows base (blue) and instruct (orange) side by side.

FRAME 2 (3-6s): Green arrow appears on Rubric Order  value drops 44%
  Text: "Rubric Order Bias: -44%"

FRAME 3 (6-9s): Green arrow appears on Score ID  value drops 77%
  Text: "Score ID Bias: -77%"

FRAME 4 (9-12s): Red arrow appears on Reference Answer  value rises 35%
  Text: "Reference Answer Bias: +35%"

FRAME 5 (12-15s): Two channels emerge  "Format" (green) and "Content" (red)
  Text: "DIFFERENTIAL EFFECT: instruction tuning has opposite effects"

FRAME 6 (15-18s): All models, languages, probes fade in
  Text: "44 families · 5 languages · 12 probes · 118,800 judgments · $0"

The GIF will loop continuously.

To generate the actual GIF:
1. Open dashboard/surface_3d.html in a browser
2. Screen record the animation (OBS, QuickTime, etc.)
3. Convert to GIF using: ffmpeg -i input.mp4 -vf "fps=10,scale=800:-1" output.gif

Alternative: use Python with pillow:
  pip install pillow
  Then run this script.
""")

# Generate individual frames using matplotlib
try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#0f172a')

    def make_frame(frame_num):
        ax1.clear()
        ax2.clear()

        probes = ['Rubric Order', 'Score ID', 'Ref Answer']
        base_vals = [2.85, 0.67, 0.88]
        inst_vals = [1.59, 0.15, 1.19]

        # Animate values appearing progressively
        visible = min(frame_num // 15 + 1, 3)

        x = np.arange(visible)
        width = 0.35

        bars1 = ax1.bar(x - width/2, base_vals[:visible], width, label='Base', color='#60a5fa')
        bars2 = ax1.bar(x + width/2, inst_vals[:visible], width, label='Instruct', color='#f59e0b')

        ax1.set_xticks(x)
        ax1.set_xticklabels(probes[:visible], color='white')
        ax1.set_ylabel('Bias (Δ)', color='white')
        ax1.set_title('Scoring Bias: Base vs Instruct', color='white', fontsize=14)
        ax1.legend()
        ax1.set_facecolor('#1e293b')
        ax1.tick_params(colors='white')

        # Percentage changes
        if visible >= 2:
            changes = [-44, -77, 35]
            for i in range(visible):
                color = '#22c55e' if changes[i] < 0 else '#ef4444'
                ax1.text(i, max(base_vals[i], inst_vals[i]) + 0.3,
                        f'{changes[i]:+d}%', ha='center', color=color, fontweight='bold')

        # Right panel: key insight
        ax2.text(0.5, 0.7, 'DIFFERENTIAL EFFECT', fontsize=16, fontweight='bold',
                color='#fbbf24', ha='center', transform=ax2.transAxes)
        ax2.text(0.5, 0.5, 'Format biases ↓   Content biases ↑', fontsize=14,
                color='#94a3b8', ha='center', transform=ax2.transAxes)
        ax2.text(0.5, 0.3, f'{visible}/3 probes shown', fontsize=12,
                color='#64748b', ha='center', transform=ax2.transAxes)
        ax2.axis('off')
        ax2.set_facecolor('#1e293b')

        plt.tight_layout()

    # Create animation
    anim = animation.FuncAnimation(fig, make_frame, frames=45, interval=200)

    # Save as GIF
    anim.save(OUT, writer='pillow', fps=5, dpi=100)
    print(f"Video abstract saved: {OUT}")

except ImportError:
    print("matplotlib not available. Install with: pip install matplotlib")
    print("Or use the screen-record approach described above.")

print("="*60)
