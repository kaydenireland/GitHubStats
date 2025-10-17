from collections import defaultdict
from pathlib import Path
import requests
import matplotlib.pyplot as plt
import json
import sys


# ------------------------
# Data Gathering
# ------------------------

def get_base_directory():
    return Path(__file__).resolve().parent

def save_to_json(lang_data: dict, save_path: str):
    file_name = save_path

    if save_path:
        with open(file_name, 'w') as f:
            json.dump(lang_data, f, indent=4)

def load_from_json(path: str):
    if path:
        with open(path, 'r') as f:
            data = json.load(f)
        # force counts to ints
        return {lang: int(count) for lang, count in data.items()}
    return {}

# ------------------------
# Centralized Processing
# ------------------------

def process_lang_data(lang_data: dict, color_file: str, min_pct: float = 0.015):
    if not lang_data:
        return []

    total_bytes = sum(lang_data.values())
    major = []
    minor_total = 0

    with open(color_file, "r") as f:
        color_map = json.load(f)

    for lang, count in lang_data.items():
        if count / total_bytes >= min_pct:
            major.append({
                "label": lang,
                "size": count,
                "color": color_map.get(lang, {}).get("color", "#CCCCCC")
            })
        else:
            minor_total += count

    if minor_total > 0:
        major.append({
            "label": "Other",
            "size": minor_total,
            "color": "#000000"
        })

    major.sort(key=lambda x: x["size"], reverse=True)
    return major

# ------------------------
# Chart Renderers
# ------------------------

def create_pie_chart(username: str, lang_data: dict, min_pct: float, color_file_path: str):
    data = process_lang_data(lang_data, color_file_path, min_pct)

    total = sum(d["size"] for d in data)

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, _ = ax.pie([d["size"] for d in data], colors=[d["color"] for d in data])
    ax.legend(
        wedges,
        [f"{d['label']} - {d['size'] / total:.1%}" for d in data],
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    ax.set_title(f"{username}'s Most Used Languages")
    return fig, ax

def create_donut_chart(username: str, lang_data: dict, min_pct: float, dh_width: float, color_file_path: str):
    data = process_lang_data(lang_data, color_file_path, min_pct)

    total = sum(d["size"] for d in data)

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, _ = ax.pie([d["size"] for d in data], colors=[d["color"] for d in data], wedgeprops=dict(width=dh_width))
    ax.legend(
        wedges,
        [f"{d['label']} - {d['size'] / total:.1%}" for d in data],
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )
    ax.set_title(f"{username}'s Most Used Languages")
    return fig, ax


def create_vertical_bar_chart(username: str, lang_data: dict, min_pct: float, color_file_path: str):
    data = process_lang_data(lang_data, color_file_path, min_pct)
    total = sum(d["size"] for d in data)

    fig, ax = plt.subplots(figsize=(8, 6))

    bars = ax.bar([d["label"] for d in data],
                  [d["size"] / 1_000 for d in data],  # Y-axis in MB
                  color=[d["color"] for d in data])

    ax.set_ylabel("Kilobytes")  # left axis label
    ax.set_title(f"{username}'s Most Used Languages")

    # Legend showing percentage
    ax.legend(bars, [f"{d['label']} - {d['size'] / total:.1%}" for d in data],
              loc="center left", bbox_to_anchor=(1, 0.5))

    return fig, ax

def create_horizontal_bar_chart(username: str, lang_data: dict, min_pct: float, color_file_path: str):
    data = process_lang_data(lang_data, color_file_path, min_pct)
    total = sum(d["size"] for d in data)

    fig, ax = plt.subplots(figsize=(8, max(2, len(data)*0.5)))  # dynamic height

    bars = ax.barh([d["label"] for d in data],
                   [d["size"]/1_000 for d in data],  # X-axis in KB
                   color=[d["color"] for d in data])

    ax.set_xlabel("Kilobytes")  # X-axis label
    ax.set_title(f"{username}'s Most Used Languages")

    # Legend showing percentage
    ax.legend(bars, [f"{d['label']} - {d['size']/total:.1%}" for d in data],
              loc="center left", bbox_to_anchor=(1, 0.5))

    # Optionally invert Y-axis for top-to-bottom ranking
    ax.invert_yaxis()

    return fig, ax

def create_stacked_chart(username: str, lang_data: dict, min_pct: float, color_file_path: str):
    data = process_lang_data(lang_data, color_file_path, min_pct)
    total = sum(d["size"] for d in data)

    fig, ax = plt.subplots(figsize=(8, 1.5))  # smaller height for a sleek bar
    left = 0
    for d in data:
        width = d["size"] / total
        ax.barh(0, width, left=left, color=d["color"], edgecolor=d["color"], height=1.0)
        left += width

    # Remove axes
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Legend
    ax.legend([f"{d['label']} - {d['size'] / total:.1%}" for d in data],
              loc="center left", bbox_to_anchor=(1, 0.5))

    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title(f"{username}'s Most Used Languages")
    return fig, ax

# ------------------------
# Save/Show
# ------------------------

def save_chart_to_file(fig, path: str, dpi: int = 300):
    fig.savefig(path, bbox_inches="tight", dpi=dpi)
    plt.close(fig)
    print(f"[LOG] Chart Saved to {path}")

def show_chart(fig):
    # display chart
    fig.show()


# ------------------------
# Factory
# ------------------------

def create_chart(type: str, username: str, lang_data: dict, minimum_percentage: float, dh_width: float, color_file_path: str):
    if type == "pie":
        fig, ax = create_pie_chart(username, lang_data, minimum_percentage, color_file_path)
    elif type == "donut":
        fig, ax = create_donut_chart(username, lang_data, minimum_percentage, dh_width, color_file_path)
    elif type == "vbar":
        fig, ax = create_vertical_bar_chart(username, lang_data, minimum_percentage, color_file_path)
    elif type == "hbar":
        fig, ax = create_horizontal_bar_chart(username, lang_data, minimum_percentage, color_file_path)
    elif type == "stacked":
        fig, ax = create_stacked_chart(username, lang_data, minimum_percentage, color_file_path)
    else:
        print("[LOG/ERROR] Invalid Chart Type (chart_type)")
        return
    return fig, ax

def output_chart(output_option: str, image_save_path: str, fig):
    if output_option == "save":
        print("[LOG] Saving Chart")
        save_chart_to_file(fig, image_save_path)
    elif output_option == "show":
        print("[LOG] Showing Chart")
        show_chart(fig)
    else:
        print("[LOG/ERROR] Invalid Output Type (output_option)")
