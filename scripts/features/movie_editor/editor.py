import logging
import platform

import cv2
import modules
import modules.scripts as scripts
import numpy as np
import pandas
import PIL
from modules import deepbooru, processing, shared
from modules.processing import Processed, process_images
from modules.shared import state
from PIL import Image
from tqdm import tqdm

from ebsynth import Keyframe
from ebsynth.ebsynth_generate import EbsynthGenerate
from scripts.m2m_util import get_mov_all_images, save_video

logger = logging.getLogger("mov2mov")

scripts_mov2mov = scripts.ScriptRunner()

# UI logic


def interrogate_keyframe(self, data_frame: pandas.DataFrame):
    """
    Interrogate key frame
    """
    bar = tqdm(total=len(data_frame))
    for index, row in data_frame.iterrows():
        if row["frame"] <= 0:
            continue
        bar.set_description(f'Interrogate key frame {row["frame"]}')
        frame = row["frame"] - 1
        image = self.frames[frame]
        image = Image.fromarray(image)
        prompt = shared.interrogator.interrogate(image.convert("RGB"))
        data_frame.at[index, "prompt"] = prompt
        bar.update(1)

    return data_frame


def deepbooru_keyframe(self, data_frame: pandas.DataFrame):
    """
    Deepbooru key frame

    """
    bar = tqdm(total=len(data_frame))
    for index, row in data_frame.iterrows():
        if row["frame"] <= 0:
            continue
        bar.set_description(f'Interrogate key frame {row["frame"]}')
        frame = row["frame"] - 1
        image = self.frames[frame]
        image = Image.fromarray(image)
        prompt = deepbooru.model.tag(image)
        data_frame.at[index, "prompt"] = prompt
        bar.update(1)

    return data_frame


def add_keyframe_click(self, data_frame: pandas.DataFrame, gr_frame_number: int):
    """
    Add a key frame to the data frame
    """
    if gr_frame_number < 1:
        return data_frame

    data_frame = data_frame[data_frame["frame"] > 0]

    if gr_frame_number in data_frame["frame"].values:
        return data_frame

    row = {"id": len(data_frame), "frame": gr_frame_number, "prompt": ""}
    data_frame.loc[len(data_frame)] = row

    data_frame = data_frame.sort_values(by="frame").reset_index(drop=True)

    data_frame["id"] = range(len(data_frame))

    return data_frame


def remove_keyframe_click(self, data_frame: pandas.DataFrame):
    """
    Remove the selected key frame
    """
    if self.selected_data_frame < 0:
        return data_frame

    data_frame = data_frame.drop(self.selected_data_frame)

    data_frame = data_frame.sort_values(by="frame").reset_index(drop=True)

    data_frame["id"] = range(len(data_frame))

    return data_frame


def key_frame_interval_generate_click(
    self, data_frame: pandas.DataFrame, key_frame_interval: int
):
    if key_frame_interval < 1:
        return data_frame

    # 按照key_frame_interval的间隔添加关键帧
    for i in range(0, self.frame_count, key_frame_interval):
        data_frame = self.add_keyframe_click(data_frame, i + 1)

    # 添加最后一帧
    data_frame = self.add_keyframe_click(data_frame, self.frame_count)

    return data_frame


# Generation logic


def process_keyframes(p, mov_file, fps, df, args):
    processing.fix_seed(p)
    images = get_mov_all_images(mov_file, fps)
    if not images:
        logger.warning("Failed to parse the video, please check")
        return

    # 通过宽高,缩放模式,预处理图片
    images = [PIL.Image.fromarray(image) for image in images]
    images = [
        modules.images.resize_image(p.resize_mode, image, p.width, p.height)
        for image in images
    ]
    images = [np.asarray(image) for image in images]

    default_prompt = p.prompt
    max_frames = len(df)

    p.do_not_save_grid = True
    state.job_count = max_frames  # * p.n_iter
    generate_images = []

    for i, row in df.iterrows():
        p.prompt = default_prompt + row["prompt"]
        frame = images[row["frame"] - 1]

        state.job = f"{i + 1} out of {max_frames}"
        if state.skipped:
            state.skipped = False

        if state.interrupted:
            break

        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), "RGB")
        p.init_images = [img]
        proc = scripts_mov2mov.run(p, *args)
        if proc is None:
            print(f"current progress: {i + 1}/{max_frames}")
            processed = process_images(p)
            gen_image = processed.images[0]

            if gen_image.height != p.height or gen_image.width != p.width:
                logger.warning(
                    f"The generated image size is inconsistent with the original image size, "
                    f"please check the configuration parameters"
                )
                gen_image = gen_image.resize((p.width, p.height))

            keyframe = Keyframe(row["frame"], np.asarray(gen_image), row["prompt"])
            generate_images.append(keyframe)

    # 由于生成图片可能会产生像素偏差,这里再对齐一次宽高
    images = [PIL.Image.fromarray(image) for image in images]
    images = [
        (
            image.resize(p.width, p.height)
            if image.width != p.width or image.height != p.height
            else image
        )
        for image in images
    ]
    images = [np.asarray(image) for image in images]

    return generate_images, images


def process_mov2mov_ebsynth(p, eb_generate, weight=4.0):
    from ebsynth._ebsynth import task as EbsyncthRun

    tasks = eb_generate.get_tasks(weight)
    tasks_len = len(tasks)
    state.job_count = tasks_len  # * p.n_iter

    for i, task in tqdm(enumerate(tasks)):

        state.job = f"{i + 1} out of {tasks_len}"
        if state.skipped:
            state.skipped = False

        if state.interrupted:
            break

        result = EbsyncthRun(task.style, [(task.source, task.target, task.weight)])
        eb_generate.append_generate_frames(task.key_frame_num, task.frame_num, result)
        state.nextjob()

    logging.info(f"Start merge frames")
    result = eb_generate.merge_sequences()
    video = save_video(result, eb_generate.fps, None, None, None)
    return video


def check_data_frame(df: pandas.DataFrame):
    # 删除df的frame值为0的行
    df = df[df["frame"] > 0]

    # 判断df是否为空
    if len(df) <= 0:
        return False

    return True


def process_movie_editor_mov2mov(
    p,
    mov_file,
    movie_frames,
    df: pandas.DataFrame,
    eb_weight,
    args,
):
    # editor
    if platform.system() != "Windows":
        raise Exception("The Movie Editor is currently only supported on Windows")

    # check df no frame
    if not check_data_frame(df):
        raise Exception("Please add a frame in the Movie Editor or disable it")

    # sort df for index
    df = df.sort_values(by="frame").reset_index(drop=True)

    # generate keyframes
    logging.info(f"Start generate keyframes")
    keyframes, frames = process_keyframes(p, mov_file, movie_frames, df, args)
    eb_generate = EbsynthGenerate(keyframes, frames, movie_frames)
    logging.info(f"\nStart generate frames")

    generate_video = process_mov2mov_ebsynth(p, eb_generate, weight=eb_weight)

    processed = Processed(p, [], p.seed, "")
    return generate_video, processed
