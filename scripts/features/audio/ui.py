import gradio as gr
from scripts.audio_transformers.voice_pitcher import generate_pitched_audio


class AudioUI:
    def __init__(self, id_part):
        self.id_part = id_part

    def render(self, init_mov):
        with gr.Accordion(
            label="Audio Layer", elem_id=f"{self.id_part}_audio_accordion", open=False
        ):
            reuse_audio = gr.Checkbox(
                label="Reuse audio from input video",
                elem_id=f"{self.id_part}_reuse_audio",
                value=True,
            )
            audio = gr.Audio(
                label="Audio for mov2mov",
                elem_id=f"{self.id_part}_audio",
                source="upload",
                visible=False,
            )
            reuse_audio.change(
                lambda checked: gr.update(visible=not checked),
                inputs=reuse_audio,
                outputs=audio,
            )
            with gr.Row():
                pitch_audio = gr.Checkbox(
                    label="Pitch audio",
                    elem_id=f"{self.id_part}_pitch_audio",
                    value=False,
                )
                pitch_step = gr.Number(
                    label="Pitch step (default is 1)",
                    minimum=0,
                    maximum=3,
                    value=1,
                    precision=None,
                    elem_id=f"{self.id_part}_pitch_step",
                )
                pitched_audio = gr.Audio(
                    label="Pitched Audio",
                    type="filepath",
                    elem_id=f"{self.id_part}_pitched_audio",
                )

                # Bind events
                pitch_audio.change(
                    fn=generate_pitched_audio,
                    inputs=[init_mov, audio, reuse_audio, pitch_step],
                    outputs=pitched_audio,
                )

                pitch_step.change(
                    fn=generate_pitched_audio,
                    inputs=[init_mov, audio, reuse_audio, pitch_step],
                    outputs=pitched_audio,
                )
        return [reuse_audio, audio, pitch_audio, pitched_audio]
