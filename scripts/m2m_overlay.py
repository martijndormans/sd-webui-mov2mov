import sys
import cv2
import numpy as np
import imageio
import os

def overlay_watermark_on_video(input_video, watermark_img, output_video, audio_path=None, audio_bitrate="68k", video_bitrate="2454k", scale=0.5, margin=20):
    watermark = cv2.imread(watermark_img, cv2.IMREAD_UNCHANGED)
    if watermark is None:
        raise ValueError("Could not load watermark image.")

    cap = cv2.VideoCapture(input_video)
    if not cap.isOpened():
        raise ValueError("Could not open input video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    wm_width = int(width * scale)
    wm_height = int(watermark.shape[0] * (wm_width / watermark.shape[1]))
    watermark_resized = cv2.resize(watermark, (wm_width, wm_height), interpolation=cv2.INTER_AREA)

    if watermark_resized.shape[2] == 4:
        wm_bgr = watermark_resized[:, :, :3]
        wm_alpha = watermark_resized[:, :, 3] / 255.0
    else:
        wm_bgr = watermark_resized
        wm_alpha = np.ones((wm_height, wm_width), dtype=np.float32)

    x_offset = width - wm_width - margin
    y_offset = height - wm_height - margin

    writer_kwargs = dict(format='ffmpeg', mode='I', fps=fps, codec='libx264')
    ffmpeg_params = []
    if audio_path:
        writer_kwargs['audio_path'] = audio_path
        ffmpeg_params += ['-b:a', audio_bitrate]
    if video_bitrate:
        ffmpeg_params += ['-b:v', video_bitrate]
    if ffmpeg_params:
        writer_kwargs['ffmpeg_params'] = ffmpeg_params

    with imageio.v2.get_writer(output_video, **writer_kwargs) as writer:
        for _ in range(frame_count):
            ret, frame = cap.read()
            if not ret:
                break

            roi = frame[y_offset:y_offset+wm_height, x_offset:x_offset+wm_width]
            blended = (wm_alpha[..., None] * wm_bgr + (1 - wm_alpha[..., None]) * roi).astype(np.uint8)
            frame[y_offset:y_offset+wm_height, x_offset:x_offset+wm_width] = blended

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            writer.append_data(frame_rgb)

    cap.release()