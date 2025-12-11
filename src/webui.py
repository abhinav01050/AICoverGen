import json
import os
import shutil
import zipfile
from argparse import ArgumentParser
import gradio as gr
from main import song_cover_pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mdxnet_models_dir = os.path.join(BASE_DIR, 'mdxnet_models')
rvc_models_dir = os.path.join(BASE_DIR, 'rvc_models')
output_dir = os.path.join(BASE_DIR, 'song_output')

def get_current_models(models_dir):
    models_list = os.listdir(models_dir)
    items_to_remove = ['hubert_base.pt', 'MODELS.txt', 'public_models.json', 'rmvpe.pt']
    return [item for item in models_list if item not in items_to_remove]

def update_models_list():
    models_l = get_current_models(rvc_models_dir)
    return gr.Dropdown.update(choices=models_l)

# Model download/upload functions omitted for brevity; unchanged
# ... use your previous download_online_model, upload_local_model, etc.

custom_head = '''
<title>🎤 AI Cover Generator - Transform Your Voice 🎵</title>
<link rel="icon" href="/favicon.ico" type="image/x-icon">
'''

if __name__ == '__main__':
    parser = ArgumentParser(description='AI Cover Generator file upload only WebUI.', add_help=True)
    parser.add_argument("--share", action="store_true", dest="share_enabled", default=False, help="Enable sharing")
    parser.add_argument("--listen", action="store_true", default=False, help="Make the WebUI reachable from your local network.")
    parser.add_argument('--listen-host', type=str, help='The hostname that the server will use.')
    parser.add_argument('--listen-port', type=int, help='The listening port that the server will use.')
    args = parser.parse_args()

    voice_models = get_current_models(rvc_models_dir)
    with open(os.path.join(rvc_models_dir, 'public_models.json'), encoding='utf8') as infile:
        public_models = json.load(infile)

    with gr.Blocks(
        title="🎤 AI Cover Generator - Transform Your Voice 🎵",
        head=custom_head,
        css="footer{display:none !important}" # Remove Gradio & API attribution
    ) as app:
        # Bold and centered title HTML
        gr.HTML('<h1 style="text-align: center; font-weight: bold; font-size: 2.2em; margin-bottom: 8px;">🎤 AI Cover Generator - Transform Your Voice 🎵</h1>')

        # --- Main demo tab ---
        with gr.Tab("Generate"):
            with gr.Accordion('Main Options'):
                with gr.Row():
                    with gr.Column():
                        rvc_model = gr.Dropdown(voice_models, label='Voice Models', info='Models folder "AICoverGen --> rvc_models".')
                        ref_btn = gr.Button('Refresh Models 🔁', variant='primary')
                    with gr.Column():
                        local_file = gr.File(label='Upload your Audio file')
                    with gr.Column():
                        pitch = gr.Slider(-3, 3, value=0, step=1, label='Pitch Change (Vocals ONLY)', info='Use 1 for male to female conversion, -1 for vice-versa.')
                        pitch_all = gr.Slider(-12, 12, value=0, step=1, label='Overall Pitch Change (Semitones)')

            with gr.Accordion('Voice conversion options', open=False):
                with gr.Row():
                    index_rate = gr.Slider(0, 1, value=0.5, label='Index Rate')
                    filter_radius = gr.Slider(0, 7, value=3, step=1, label='Filter radius')
                    rms_mix_rate = gr.Slider(0, 1, value=0.25, label='RMS mix rate')
                    protect = gr.Slider(0, 0.5, value=0.33, label='Protect rate')
                    with gr.Column():
                        f0_method = gr.Dropdown(['rmvpe', 'mangio-crepe'], value='rmvpe', label='Pitch detection algorithm')
                        crepe_hop_length = gr.Slider(32, 320, value=128, step=1, visible=False, label='Crepe hop length')
                        f0_method.change(
                            lambda algo: gr.update(visible=(algo == 'mangio-crepe')),
                            inputs=f0_method, outputs=crepe_hop_length
                        )
                keep_files = gr.Checkbox(label='Keep intermediate files')

            with gr.Accordion('Audio mixing options', open=False):
                gr.Markdown('### Volume Change (decibels)')
                with gr.Row():
                    main_gain = gr.Slider(-20, 20, value=0, step=1, label='Main Vocals')
                    backup_gain = gr.Slider(-20, 20, value=0, step=1, label='Backup Vocals')
                    inst_gain = gr.Slider(-20, 20, value=0, step=1, label='Music')
                gr.Markdown('### Reverb Control on AI Vocals')
                with gr.Row():
                    reverb_rm_size = gr.Slider(0, 1, value=0.15, label='Room size')
                    reverb_wet = gr.Slider(0, 1, value=0.2, label='Wetness level')
                    reverb_dry = gr.Slider(0, 1, value=0.8, label='Dryness level')
                    reverb_damping = gr.Slider(0, 1, value=0.7, label='Damping level')
                gr.Markdown('### Audio Output Format')
                output_format = gr.Dropdown(['mp3', 'wav'], value='mp3', label='Output file type')

            with gr.Row():
                clear_btn = gr.ClearButton(value='Clear', components=[rvc_model, keep_files, local_file])
                generate_btn = gr.Button("Generate", variant='primary')
                ai_cover = gr.Audio(label='AI Cover', show_share_button=False)

            ref_btn.click(update_models_list, None, outputs=rvc_model)
            is_webui = gr.Number(value=1, visible=False)

            def safe_song_cover_pipeline(local_file, rvc_model, pitch, keep_files, is_webui, main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length, protect, pitch_all, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping, output_format):
                if local_file is None or not os.path.isfile(local_file.name):
                    raise gr.Error("Please upload a valid audio file (.mp3/.wav) before generating.")
                return song_cover_pipeline(
                    local_file.name, rvc_model, pitch, keep_files, is_webui, main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length, protect, pitch_all, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping, output_format
                )

            generate_btn.click(
                safe_song_cover_pipeline,
                inputs=[local_file, rvc_model, pitch, keep_files, is_webui, main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate, f0_method, crepe_hop_length, protect, pitch_all, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping, output_format],
                outputs=[ai_cover]
            )
            clear_btn.click(lambda: [0, 0, 0, 0, 0.5, 3, 0.25, 0.33, 'rmvpe', 128, 0, 0.15, 0.2, 0.8, 0.7, 'mp3', None], outputs=[pitch, main_gain, backup_gain, inst_gain, index_rate, filter_radius, rms_mix_rate, protect, f0_method, crepe_hop_length, pitch_all, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping, output_format, ai_cover])

        # --- Other tabs (Download Model, Upload Model) can remain unchanged ---

    app.launch(
        share=args.share_enabled,
        enable_queue=True,
        server_name=None if not args.listen else (args.listen_host or '0.0.0.0'),
        server_port=args.listen_port,
    )
