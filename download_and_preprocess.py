import argparse
import os
import re
from pathlib import Path
import subprocess
import pyzstd

from enums import Folders


def download_data(year, month, source):
    if source != "lichess-open-database":
        raise ValueError(
            "Source must be lichess-open-database. Support for additional sources will be added in the future."
        )

    year = str(year)
    month = str(month).zfill(2)
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{year}-{month}.pgn.zst"
    filename = f"lichess_db_standard_rated_{year}-{month}.pgn.zst"
    if not os.path.exists(Folders.LICHESS_DOWNLOADED_GAMES.value):
        os.mkdir(Folders.LICHESS_DOWNLOADED_GAMES.value)

    # Check file size before downloading
    response = subprocess.run(
        ["wget", "--spider", "--server-response", url],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    # print(f"response: {response}")
    result = re.search("Content-Length: (.*)\n", response.stderr.decode())
    content_length = result.group(1) if result else None
    download_file_size = int(content_length) if content_length.isdigit() else None

    # Warn user if file size exceeds 1 GB
    if download_file_size and download_file_size > 10**9:
        user_response = input(
            "Warning: File size exceeds 1GB. Do you want to proceed with the download? (Y/N): "
        )
        if user_response.lower() != "y":
            print("Download aborted.")
            return None
        else:
            subprocess.run(["wget", url, "-P", Folders.LICHESS_DOWNLOADED_GAMES.value])
    else:
        subprocess.run(["wget", url, "-P", Folders.LICHESS_DOWNLOADED_GAMES.value])

    return filename


def preprocess_data(filename, remove_raw_files):
    """This function calls parse_pgn.py and make_player_features.py with pgn and csv filepaths"""

    BASE_FILE_NAME = Path(filename).stem.split(".")[
        0
    ]  ## removes .pgn.zst from extension
    PGN_FILE_PATH = f"{Folders.LICHESS_DOWNLOADED_GAMES.value}/{BASE_FILE_NAME}.pgn"
    ZST_FILE_PATH = f"{Folders.LICHESS_DOWNLOADED_GAMES.value}/{BASE_FILE_NAME}.pgn.zst"

    # decompress .pgn.zst and save as .pgn
    with open(ZST_FILE_PATH, "rb") as f_in:
        compressed_data = f_in.read()

    decompressed_data = pyzstd.decompress(compressed_data)

    with open(PGN_FILE_PATH, "wb") as f_out:
        f_out.write(decompressed_data)

    subprocess.run(["python3", "parse_pgn.py", PGN_FILE_PATH])

    CSV_RAW_FEATURES_FILE_PATH = (
        f"{Folders.LICHESS_PLAYER_DATA.value}/{BASE_FILE_NAME}.csv"
    )
    subprocess.run(["python3", "make_player_features.py", CSV_RAW_FEATURES_FILE_PATH])

    ## make exploratory plots
    CSV_PLAYER_FEATURE_FILE_PATH = (
        f"{Folders.LICHESS_PLAYER_DATA.value}/{BASE_FILE_NAME}_player_features.csv"
    )
    subprocess.run(
        ["python3", "make_exploratory_plots.py", CSV_PLAYER_FEATURE_FILE_PATH]
    )

    # Remove the downloaded .pgn.zst and .pgn files
    if remove_raw_files:
        print("Cleaning up downloaded files...")
        os.remove(PGN_FILE_PATH)
        os.remove(ZST_FILE_PATH)


def main():
    parser = argparse.ArgumentParser(description="Download and preprocess Lichess data")
    parser.add_argument("--year", type=int, help="Year of the data", required=True)
    parser.add_argument("--month", type=int, help="Month of the data", required=True)
    parser.add_argument(
        "--source",
        type=str,
        help="Source of the file to download",
        choices=["lichess-open-database"],
        required=True,
    )
    parser.add_argument(
        "--generate-exploratory-plots",
        action="store_true",
        help="Generate exploratory plots",
    )
    parser.add_argument(
        "--remove-raw-files",
        action="store_true",
        help="Remove raw files after preprocessing",
    )
    args = parser.parse_args()

    filename = download_data(args.year, args.month, args.source)
    preprocess_data(filename, args.remove_raw_files)


if __name__ == "__main__":
    main()
