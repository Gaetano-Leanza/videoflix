import os
import subprocess
from .models import Video


def convert_video_to_hls(video_id):
    # Das Video aus der Datenbank abrufen
    video = Video.objects.get(id=video_id)
    source_path = video.video_file.path

    base_dir = os.path.dirname(source_path)

    video_dir = os.path.join(base_dir, str(video.id))
    os.makedirs(video_dir, exist_ok=True)

    resolutions = {
        '480p': 480,
        '720p': 720,
        '1080p': 1080
    }

    for res_name, height in resolutions.items():

        res_dir = os.path.join(video_dir, res_name)
        os.makedirs(res_dir, exist_ok=True)

        output_m3u8 = os.path.join(res_dir, 'index.m3u8')

        output_ts = os.path.join(res_dir, '%03d.ts')

        cmd = [
            'ffmpeg',
            '-i', source_path,
            '-vf', f'scale=-2:{height}',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-hls_time', '10',
            '-hls_playlist_type', 'vod',
            '-hls_segment_filename', output_ts,
            output_m3u8
        ]

        subprocess.run(cmd, check=True)
