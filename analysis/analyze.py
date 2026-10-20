"""Parse the raw GI benchmark CSVs and produce summary stats and figures.

The CSVs were written with a comma decimal separator *and* a comma field
separator, so a row such as ``12,99,4,373,228,67,RC`` means
time=12.99 s, frame=4.373 ms, fps=228.67, mode=RC. This script undoes that.

Usage:
    uv run analyze [--warmup 5]
"""

import argparse
import re
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "Measured Data"
OUT_DIR = Path(__file__).resolve().parent / "output"

SCENES = {
    "Isometric": "Isometric",
    "Realistic FPS": "Realistic",
    "Stylized Fps": "Stylized",
}
MODES = ["NoGI", "RTLM", "SSGI", "RC"]
MODE_LABELS = {
    "NoGI": "No GI",
    "RTLM": "Realtime Lightmaps",
    "SSGI": "Screen Space GI",
    "RC": "Radiance Cascades",
}
COLORS = {"NoGI": "#8a8a8a", "RTLM": "#4c78a8", "SSGI": "#f58518", "RC": "#e45756"}


def parse_run(path):
    """Return a list of (time_sec, ms_per_frame) samples from one CSV."""
    samples = []
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.strip().split(",")
        if len(parts) != 7:
            continue  # blank line or SUMMARY footer
        t = float(f"{parts[0]}.{parts[1]}")
        ms = float(f"{parts[2]}.{parts[3]}")
        samples.append((t, ms))
    return samples


def percentile(values, p):
    ordered = sorted(values)
    k = (len(ordered) - 1) * p / 100
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo)


def summarize(frame_ms):
    return {
        "avg_ms": statistics.mean(frame_ms),
        "p95_ms": percentile(frame_ms, 95),
        "p99_ms": percentile(frame_ms, 99),
        "avg_fps": 1000 / statistics.mean(frame_ms),
        "low1_fps": 1000 / percentile(frame_ms, 99),
        "stdev_ms": statistics.stdev(frame_ms),
    }


def load_all():
    runs = {}
    for folder, scene in SCENES.items():
        for path in sorted((DATA_DIR / folder).glob("gi_run_*.csv")):
            # Take the mode from the file name; one file labels RTLM as "RILM".
            mode = re.match(r"gi_run_([A-Za-z]+)_", path.name).group(1)
            runs[(scene, mode)] = parse_run(path)
    return runs


def plot_frame_times(runs, warmup):
    fig, axes = plt.subplots(len(SCENES), 1, figsize=(10, 9), sharex=True)
    for ax, scene in zip(axes, SCENES.values()):
        for mode in MODES:
            samples = [(t, ms) for t, ms in runs[(scene, mode)] if t >= warmup]
            ax.plot(
                [t for t, _ in samples],
                [ms for _, ms in samples],
                label=MODE_LABELS[mode],
                color=COLORS[mode],
                linewidth=1,
            )
        ax.set_title(scene)
        ax.set_ylabel("Frame time (ms)")
        ax.grid(alpha=0.3)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=8)
    axes[-1].set_xlabel("Time (s)")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT_DIR / "frame_time_over_time.png", dpi=150)
    plt.close(fig)


def plot_fps_bars(stats):
    scenes = list(SCENES.values())
    width = 0.2
    fig, ax = plt.subplots(figsize=(10, 5))
    for i, mode in enumerate(MODES):
        xs = [s + (i - 1.5) * width for s in range(len(scenes))]
        avg = [stats[(scene, mode)]["avg_fps"] for scene in scenes]
        low = [stats[(scene, mode)]["low1_fps"] for scene in scenes]
        ax.bar(xs, avg, width, label=MODE_LABELS[mode], color=COLORS[mode])
        ax.scatter(xs, low, color="black", marker="_", s=200, zorder=3)
        for x, v in zip(xs, avg):
            ax.text(x, v + 3, f"{v:.0f}", ha="center", fontsize=8)
    ax.set_xticks(range(len(scenes)))
    ax.set_xticklabels(scenes)
    ax.set_ylabel("FPS (bar = average, tick = 1% low)")
    ax.legend(ncol=4, fontsize=8, loc="lower center", bbox_to_anchor=(0.5, 1.0))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fps_comparison.png", dpi=150)
    plt.close(fig)


def plot_distribution(runs, warmup):
    fig, axes = plt.subplots(1, len(SCENES), figsize=(12, 4), sharey=True)
    for ax, scene in zip(axes, SCENES.values()):
        data = [[ms for t, ms in runs[(scene, m)] if t >= warmup] for m in MODES]
        box = ax.boxplot(data, patch_artist=True, showfliers=False)
        for patch, mode in zip(box["boxes"], MODES):
            patch.set_facecolor(COLORS[mode])
        ax.set_xticks(range(1, len(MODES) + 1))
        ax.set_xticklabels(MODES)
        ax.set_title(scene)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Frame time (ms)")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "frame_time_distribution.png", dpi=150)
    plt.close(fig)


def write_tables(stats):
    with open(OUT_DIR / "summary.csv", "w", encoding="utf-8") as f:
        f.write("scene,mode,avg_fps,low1_fps,avg_ms,p95_ms,p99_ms,stdev_ms,cost_vs_nogi_ms\n")
        for scene in SCENES.values():
            base = stats[(scene, "NoGI")]["avg_ms"]
            for mode in MODES:
                s = stats[(scene, mode)]
                f.write(
                    f"{scene},{mode},{s['avg_fps']:.1f},{s['low1_fps']:.1f},"
                    f"{s['avg_ms']:.3f},{s['p95_ms']:.3f},{s['p99_ms']:.3f},"
                    f"{s['stdev_ms']:.3f},{s['avg_ms'] - base:+.3f}\n"
                )

    lines = [
        "| Scene | Method | Avg FPS | 1% low FPS | Avg ms | p95 ms | Cost vs No GI |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for scene in SCENES.values():
        base = stats[(scene, "NoGI")]["avg_ms"]
        for mode in MODES:
            s = stats[(scene, mode)]
            lines.append(
                f"| {scene} | {MODE_LABELS[mode]} | {s['avg_fps']:.0f} | "
                f"{s['low1_fps']:.0f} | {s['avg_ms']:.2f} | {s['p95_ms']:.2f} | "
                f"{s['avg_ms'] - base:+.2f} ms |"
            )
    table = "\n".join(lines) + "\n"
    (OUT_DIR / "summary.md").write_text(table, encoding="utf-8")
    return table


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--warmup",
        type=float,
        default=5.0,
        help="seconds to drop from the start of each run (scene loading spikes)",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    runs = load_all()
    stats = {
        key: summarize([ms for t, ms in samples if t >= args.warmup])
        for key, samples in runs.items()
    }

    plot_frame_times(runs, args.warmup)
    plot_fps_bars(stats)
    plot_distribution(runs, args.warmup)
    print(write_tables(stats))
    print(f"Figures and tables written to {OUT_DIR}")


if __name__ == "__main__":
    main()
