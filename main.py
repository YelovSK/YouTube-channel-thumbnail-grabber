from dotenv import load_dotenv
from googleapiclient.discovery import build
from rich.progress import track
import requests
import os
import shutil

load_dotenv(".env")
API_key = os.getenv("API")
youtube = build('youtube', 'v3', developerKey=API_key)


def get_channel_id(name: str) -> str:
    res = youtube.search().list(
        part="snippet",
        type="channel",
        q=name,
        key=API_key
    ).execute()
    return res["items"][0]["snippet"]["channelId"]


def get_video_ids(channel_id: str) -> list:

    res = youtube.search().list(
        part='id',
        channelId=channel_id,
        type='video',
        order='date',
        maxResults=50
    ).execute()
    next_page_token = res.get("nextPageToken")
    while "nextPageToken" in res:
        next_page = youtube.search().list(
            part='id',
            channelId=channel_id,
            type='video',
            order='date',
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        res["items"] += next_page["items"]
        if "nextPageToken" not in next_page:
            res.pop("nextPageToken", None)
        else:
            next_page_token = next_page["nextPageToken"]
    return [video["id"]["videoId"] for video in res["items"]]


def download_thumbnails(ids: list) -> None:
    print(f"Downloading {len(ids)} thumbnails")
    if os.path.exists(channel_name):
        shutil.rmtree(channel_name)
    os.mkdir(channel_name)
    for id in track(ids, description="Downloading"):
        max_res_url = f"https://i.ytimg.com/vi/{id}/maxresdefault.jpg"
        hq_res_url = f"https://i.ytimg.com/vi/{id}/hqdefault.jpg"
        request = requests.get(max_res_url)
        # check if max res available
        img = request.content if request.status_code == 200 else requests.get(hq_res_url).content
        with open(f"{channel_name}/{id}.jpg", "wb") as handler:
            handler.write(img)


if __name__ == "__main__":
    channel_name = input("Channel name >> ")
    channel_id = get_channel_id(channel_name)
    print(f"Channel ID: {channel_id}")
    video_ids = get_video_ids(channel_id)
    download_thumbnails(ids=video_ids)
