import logging
from contextlib import closing

import cv2
import gradio as gr
import modules
import modules.scripts as scripts
import pandas
from modules import processing, shared
from modules.infotext_utils import create_override_settings_dict
from modules.processing import (
    Processed,
    StableDiffusionProcessingImg2Img,
    process_images,
)
from modules.shared import opts, state
from modules.ui_common import plaintext_to_html
from PIL import Image

from scripts.features.audio.audio import choose_audio
from scripts.features.movie_editor.editor import process_movie_editor_mov2mov
from scripts.m2m_config import mov2mov_output_dir
from scripts.m2m_util import calc_video_w_h, get_mov_all_images, save_video

logger = logging.getLogger("mov2mov")

scripts_mov2mov = scripts.ScriptRunner()


def process_mov2mov(
    p, mov_file, movie_frames, max_frames, resize_mode, w, h, audio, reuse_audio, args
):
    processing.fix_seed(p)
    images = get_mov_all_images(mov_file, movie_frames)
    if not images:
        logger.warning("Failed to parse the video, please check")
        return

    logging.info(f"The video conversion is completed, images:{len(images)}")
    if max_frames == -1 or max_frames > len(images):
        max_frames = len(images)

    max_frames = int(max_frames)

    p.do_not_save_grid = True
    state.job_count = max_frames  # * p.n_iter
    generate_images = []
    for i, image in enumerate(images):
        if i >= max_frames:
            break

        state.job = f"{i + 1} out of {max_frames}"
        if state.skipped:
            state.skipped = False

        if state.interrupted:
            break

        # 存一张底图
        img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), "RGB")

        p.init_images = [img] * p.batch_size
        proc = scripts_mov2mov.run(p, *args)
        if proc is None:
            print(f"current progress: {i + 1}/{max_frames}")
            processed = process_images(p)
            # 只取第一张
            gen_image = processed.images[0]
            generate_images.append(gen_image)

    video = save_video(generate_images, movie_frames, mov_file, audio, reuse_audio)

    return video


def mov2mov(
    id_task: str,
    request: gr.Request,
    tab_index: int,
    prompt,
    negative_prompt,
    prompt_styles,
    mov_file,
    cfg_scale,
    image_cfg_scale,
    denoising_strength,
    selected_scale_tab,
    height,
    width,
    scale_by,
    resize_mode,
    override_settings_texts,
    # refiner
    # enable_refiner, refiner_checkpoint, refiner_switch_at,
    # mov2mov params
    noise_multiplier,
    movie_frames,
    max_frames,
    # mov2mov audio params
    pitch_audio,
    pitched_audio,
    reuse_audio,
    audio,
    # editor
    enable_movie_editor,
    df: pandas.DataFrame,
    eb_weight,
    *args,
):
    if not mov_file:
        raise Exception("Error！ Please add a video file!")

    if selected_scale_tab == 1:
        width, height = calc_video_w_h(mov_file)
        width = int(width * scale_by)
        height = int(height * scale_by)

    override_settings = create_override_settings_dict(override_settings_texts)
    assert 0.0 <= denoising_strength <= 1.0, "can only work with strength in [0.0, 1.0]"
    mask_blur = 4
    inpainting_fill = 1
    inpaint_full_res = False
    inpaint_full_res_padding = 32
    inpainting_mask_invert = 0

    p = StableDiffusionProcessingImg2Img(
        sd_model=shared.sd_model,
        outpath_samples=shared.opts.data.get("mov2mov_output_dir", mov2mov_output_dir),
        outpath_grids=shared.opts.data.get("mov2mov_output_dir", mov2mov_output_dir),
        prompt=prompt,
        negative_prompt=negative_prompt,
        styles=prompt_styles,
        batch_size=1,
        n_iter=1,
        cfg_scale=cfg_scale,
        width=width,
        height=height,
        init_images=[None],
        mask=None,
        mask_blur=mask_blur,
        inpainting_fill=inpainting_fill,
        resize_mode=resize_mode,
        denoising_strength=denoising_strength,
        image_cfg_scale=image_cfg_scale,
        inpaint_full_res=inpaint_full_res,
        inpaint_full_res_padding=inpaint_full_res_padding,
        inpainting_mask_invert=inpainting_mask_invert,
        override_settings=override_settings,
        initial_noise_multiplier=noise_multiplier,
    )

    p.scripts = modules.scripts.scripts_img2img
    p.script_args = args

    p.user = request.username

    if shared.opts.enable_console_prompts:
        print(f"\nmov2mov: {prompt}", file=shared.progress_print_out)

    with closing(p):
        if enable_movie_editor:
            generate_video, processed = process_movie_editor_mov2mov(
                p,
                # mov2mov simple
                mov_file,
                movie_frames,
                max_frames,
                resize_mode,
                width,
                height,
                # audio
                pitch_audio,
                pitched_audio,
                reuse_audio,
                audio,
                # editor
                enable_movie_editor,
                df,
                eb_weight,
                args,
            )
        else:
            final_audio, final_reuse_audio = choose_audio(
                pitch_audio, pitched_audio, reuse_audio, audio
            )
            print(f"\nStart parsing the number of mov frames")
            generate_video = process_mov2mov(
                p,
                mov_file,
                movie_frames,
                max_frames,
                resize_mode,
                width,
                height,
                final_audio,
                final_reuse_audio,
                args,
            )
            processed = Processed(p, [], p.seed, "")

    shared.total_tqdm.clear()

    generation_info_js = processed.js()
    if opts.samples_log_stdout:
        print(generation_info_js)

    if opts.do_not_show_images:
        processed.images = []

    return (
        generate_video,
        generation_info_js,
        plaintext_to_html(processed.info),
        plaintext_to_html(processed.comments, classname="comments"),
    )
