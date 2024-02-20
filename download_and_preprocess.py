import argparse
import os
import re
from pathlib import Path
import subprocess
import zstandard as zstd
import pyzstd

from enums import Folders


def download_data(year, month, filetype):
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
    """This function calls parse_pgn.py and make_player_features.py with the filename argument"""

    base_filename = Path(filename).stem.split(".")[
        0
    ]  ## removes .pgn.zst from extension
    PGN_FILE_PATH = f"{Folders.LICHESS_DOWNLOADED_GAMES.value}/{base_filename}.pgn"
    ZST_FILE_PATH = f"{Folders.LICHESS_DOWNLOADED_GAMES.value}/{base_filename}.pgn.zst"

    # decompress .pgn.zst and save as .pgn
    # note: for large files, this operation must be done in chunks
    # with open(ZST_FILE_PATH, "rb") as compressed_file:
    #     dctx = zstd.ZstdDecompressor()
    #     with open(PGN_FILE_PATH, "wb") as output_file:
    #         for chunk in dctx.read_to_iter(compressed_file):
    #             output_file.write(chunk)

    # with open(ZST_FILE_PATH, 'rb') as compressed_file:
    #     decompressor = zstd.ZstdDecompressor()
    #     with decompressor.stream_reader(compressed_file) as reader:
    #         with open(PGN_FILE_PATH, 'wb') as output_file:
    #             for chunk in reader:
    #                 output_file.write(chunk)

    with open(ZST_FILE_PATH, "rb") as f_in:
        compressed_data = f_in.read()

    decompressed_data = pyzstd.decompress(compressed_data)

    with open(PGN_FILE_PATH, "wb") as f_out:
        f_out.write(decompressed_data)

    subprocess.run(["python3", "parse_pgn.py", PGN_FILE_PATH])

    CSV_FILE_PATH = f"{Folders.LICHESS_PLAYER_DATA.value}/{base_filename}.csv"
    # subprocess.run(["python3", "make_player_features.py", filename[:-4]])

    # Remove the downloaded .pgn.zst and .pgn files
    if remove_raw_files:
        os.remove(PGN_FILE_PATH)
        os.remove(ZST_FILE_PATH)


def main():
    parser = argparse.ArgumentParser(description="Download and preprocess Lichess data")
    parser.add_argument("--year", type=int, help="Year of the data", required=True)
    parser.add_argument("--month", type=int, help="Month of the data", required=True)
    parser.add_argument(
        "--filetype",
        type=str,
        help="Type of file to download",
        choices=["lichess-open-database"],
        required=True,
    )
    parser.add_argument(
        "--remove-raw-files",
        action="store_true",
        help="Remove raw files after preprocessing",
    )
    args = parser.parse_args()

    filename = download_data(args.year, args.month, args.filetype)
    preprocess_data(filename, args.remove_raw_files)


if __name__ == "__main__":
    main()
