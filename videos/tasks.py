import os
import subprocess
from .models import Video

RESOLUTIONS = {'480p': 480, '720p': 720, '1080p': 1080}


def build_ffmpeg_cmd(source, target_m3u8, target_ts, height):
    return [
        'ffmpeg', '-i', source,
        '-vf', f'scale=-2:{height}',
        '-c:v', 'libx264', '-c:a', 'aac',
        '-hls_time', '10', '-hls_playlist_type', 'vod',
        '-hls_segment_filename', target_ts,
        target_m3u8
    ]


def convert_resolution(source_path, video_dir, res_name, height):
    res_dir = os.path.join(video_dir, res_name)
    os.makedirs(res_dir, exist_ok=True)
    m3u8_file = os.path.join(res_dir, 'index.m3u8')
    ts_pattern = os.path.join(res_dir, '%03d.ts')
    cmd = build_ffmpeg_cmd(source_path, m3u8_file, ts_pattern, height)
    subprocess.run(cmd, check=True)


def convert_video_to_hls(video_id):
    video = Video.objects.get(id=video_id)
    source_path = video.video_file.path
    video_dir = os.path.join(os.path.dirname(source_path), str(video.id))
    os.makedirs(video_dir, exist_ok=True)
    for res_name, height in RESOLUTIONS.items():
        convert_resolution(source_path, video_dir, res_name, height)
