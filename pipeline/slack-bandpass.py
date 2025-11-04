#!/usr/bin/env python3

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import sys
import pathlib
import os 

SLACK_TOKEN = os.getenv("SLACK_API_TOKEN")
CHANNEL_ID = 'C096N2DQ6R5'

client = WebClient(token=SLACK_TOKEN)

def upload_file_v2(file_path: pathlib.Path, title: str):
    try:
        response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=str(file_path),
            title=title,
            initial_comment=f""
        )
        if response.get("ok", False):
            print(f"Uploaded: {title}")
        else:
            print(f"Upload failed: {title} — {response}")
    except SlackApiError as e:
        print(f"Slack API error: {e.response['error']}")

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <png_directory>")
        sys.exit(1)

    png_dir = pathlib.Path(sys.argv[1])

    if not png_dir.is_dir():
        print(f"Error: {png_dir} is not a directory.")
        sys.exit(1)

    for img_path in sorted(png_dir.glob("*.png")):
        upload_file_v2(img_path, img_path.name)

if __name__ == "__main__":
    main()


