from collections import defaultdict
from pathlib import Path
import requests
import matplotlib.pyplot as plt
import json
import sys
import grapher


# ------------------------
# Data Gathering
# ------------------------

def fetch_new_langs(username: str, save_path: str = None, token : str=None):
    headers = {"Authorization": f"token {token}"} if token else {}
    lang_totals = defaultdict(int)
    page = 1

    while True:
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"

        repos = requests.get(repos_url, headers=headers).json()
        if isinstance(repos, dict) and repos.get("message"):
            raise Exception(f"Error fetching repos: {repos['message']}")
        if not repos:
            break # if there are no remaining repos

        for repo in repos:
            langs_url = repo["languages_url"]
            langs = requests.get(langs_url, headers=headers).json()
            for lang, count in langs.items():
                lang_totals[lang] += count

        page += 1

    lang_data =  dict(sorted(lang_totals.items(), key=lambda x: x[1], reverse=True))
    grapher.save_to_json(lang_data, save_path)
    return lang_data

def get_lang_data(use_data: str, username: str, token: str, data_save_path: str, chart_save_path: str):
    lang_data = defaultdict(int)

    if use_data == "new":
        print("[LOG] Getting New Data")
        lang_data = fetch_new_langs(username, data_save_path, token)
    elif use_data == "old":
        print("[LOG] Using Old Data")
        lang_data = grapher.load_from_json(chart_save_path)
    else:
        print("[LOG/ERROR] Invalid Data Selection (use_data)")
    return lang_data



def run():
    print("[LOG] Starting Script. See README for Settings Help")
    
    print("[LOG] Retrieving Base Directory")
    base_dir = grapher.get_base_directory()
    
    with open(base_dir / "settings.json", 'r') as f:
        settings = json.load(f)

    '''
    Gather All Settings
    '''
    print("[LOG] Reading Settings")
    username_setting = settings["username"]
    token_setting = settings["token"]
    data_save_path = base_dir / settings["json_save_path"]
    chart_save_path_setting = base_dir / settings["json_save_path"]
    use_data_setting = settings["use_data"]
    minimum_percentage_setting = settings["minimum_percentage"]
    chart_type_setting = settings["chart_type"]
    donut_hole_width_setting = settings["donut_hole_width"]
    output_option_setting = settings["output_option"]
    color_file_path = base_dir / "lang_colors.json"
    image_save_path_setting = base_dir / settings["image_save_path"]

    print("[LOG] Fetching Language Data")
    lang_data = get_lang_data(use_data_setting, username_setting, token_setting, data_save_path, chart_save_path_setting)

    print("[LOG] Creating Chart")
    fig, ax = grapher.create_chart(chart_type_setting, username_setting, "repo", lang_data, minimum_percentage_setting, donut_hole_width_setting, color_file_path)

    print("[LOG] Sharing Chart")
    grapher.output_chart(output_option_setting, image_save_path_setting, fig)


# ------------------------
# Main
# ------------------------

if __name__ == "__main__":
    run()
# TODO better documentation, comment entire program