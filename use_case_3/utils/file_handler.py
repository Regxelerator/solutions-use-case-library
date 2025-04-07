import json


def write_to_file(file_path: str, data):
    """
    Writes the given data to a file in JSON format.

    :param file_path: Path of the output file.
    :param data: Data to be written to the file.


    """
    try:
        with open(file_path, "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, indent=2, ensure_ascii=False)
        print(f"Data successfully written to {file_path}")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")


def read_from_file(file_path: str):
    """
    Reads data from a JSON file and returns it.

    :param file_path: Path of the JSON file to read.
    :return: Parsed JSON data if successful, None if an error occurs.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {e}")
        return None
