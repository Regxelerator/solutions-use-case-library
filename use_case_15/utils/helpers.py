import json
import os
import datetime


def log_to_csv(message, folder="logs", filename="log_file.csv"):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, filename)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a", encoding='UTF-8', errors='ignore') as file:
            file.write(f"===== {timestamp} ===== \n {message} \n")
    except Exception:
        pass


def handle_json_file(file_name: str, data: dict = None, flag: str = "save") -> dict:
    """
    Save or load a JSON file in the current directory.

    :param file_name: Name of the JSON file (e.g., 'data.json').
    :param data: Data to save (used only if flag is 'save').
    :param flag: 'save' to write data to JSON, 'load' to read data from JSON.
    :return: Loaded dict if loading, empty dict otherwise.
    """
    file_path = os.path.join(os.getcwd(), file_name)

    if flag == "save":
        if not data:
            raise ValueError("No data provided for saving.")
        with open(file_path, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=4)
        print(f"Data saved to {file_path}")
        return {}

    elif flag == "load":
        if not os.path.exists(file_path):
            print(f"⚠️ File {file_path} not found. Returning empty dict.")
            return {}
        with open(file_path, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        print(f"Data loaded from {file_path}")
        return data

    else:
        raise ValueError("Invalid flag. Use 'save' or 'load'.")
