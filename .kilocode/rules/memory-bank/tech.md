# Tech

## Technologies Used

- **Python**: Core programming language for the plugin.
- **Stable Diffusion WebUI**: Framework for integrating Mov2mov as a plugin.
- **Gradio**: Underlying framework used by Stable Diffusion WebUI for building the user interface.
- **imageio** and **imageio-ffmpeg**: Libraries for video synthesis.
- **opencv-python**: Library for video frame processing.

## Development Setup

1. Install dependencies listed in `requirements.txt`:
   ```
   pip install -r requirements.txt
   ```
2. Clone the repository and install the plugin via the WebUI Extensions tab.

## Technical Constraints

- Currently, video editing features are only supported on Windows systems.
- Temporarily removed features like modnet functionality and frame-by-frame prompt addition.

## Dependencies

- `opencv-python`
- `imageio`
- `imageio-ffmpeg`
