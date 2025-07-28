# 🚀 Mov2mov: Video-to-Video Magic for Stable Diffusion

This is a fork from: https://github.com/Scholar01/sd-webui-mov2mov

![img.png](images/2.jpg)

---

## 🎬 What is Mov2mov?

Mov2mov is a powerful plugin for [Automatic1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) that lets you transform videos frame-by-frame using AI. Effortlessly turn your videos into creative masterpieces with advanced editing features and seamless integration.

---

## ⚡ Quickstart

1. 🧩 **Install Mov2mov** via the Extensions tab in WebUI.
2. 🎥 **Load your video** in the Mov2mov panel.
3. 🖼️ **Configure your settings** (model, prompts, keyframes, audio, etc.).
4. ✨ **Start processing** and watch your video transform!
5. 📦 **Export** the processed video with audio.

---

## 🌟 Features

- 🎞️ **Directly process frames from videos**
- 📦 **Package into a video after processing**
- ✂️ **Video Editing (beta)**
  - 🔑 **Dramatically reduce video flicker by keyframe compositing!**
  - 🗝️ **Customize or auto-generate keyframes**
  - ⏪ **Backpropel keyframe tag**
  - 🪟 **Currently only available for Windows** (disable if unsupported)
- 🎵 **Add or reuse audio layers**: Overlay custom audio or reuse the original video's audio in your output!
- 🤝 **Works even better with [bg-mask](https://github.com/Scholar01/sd-webui-bg-mask) plugin!** 😃

---

## 📚 Table of Contents

- [Quickstart](#quickstart)
- [Features](#features)
- [Usage Regulations](#usage-regulations)
- [Installation](#installation)
- [Change Log](#change-log)
- [Instructions](#instructions)
- [Advanced Usage Examples](#advanced-usage-examples)
- [Audio Feature](#audio-feature)
- [Thanks](#thanks)

---

## ⚠️ Usage Regulations

1. Please resolve the authorization issues of the video source on your own. Any problems caused by using unauthorized videos for conversion must be borne by the user. It has nothing to do with mov2mov!
2. Any video made with mov2mov and published on video platforms must clearly specify the source of the video used for conversion in the description.
3. All copyright issues caused by the input source must be borne by the user.
4. Please strictly comply with national laws and regulations to ensure that the content is legal and compliant.

---

## 🛠️ Installation

1. Open the Extensions tab.
2. Click on Install from URL.
3. Enter the URL for the extension's git repository.
4. Click Install.
5. Restart WebUI.

---

## 📝 Change Log

See [`CHANGELOG.md`](CHANGELOG.md)

---

## 📖 Instructions

### Basic Workflow

1. **Load your video**: Click the "Browse" button and select your video file (supported: MP4, AVI, MOV).
2. **Set your prompts and model**: Enter your text prompt and select the desired Stable Diffusion model.
3. **Configure settings**: Adjust frame rate, resolution, and other options as needed.
4. **(Optional) Enable Video Editing**: Use the "Video Editing" tab to enable keyframe compositing for flicker reduction.
5. **(Optional) Add or reuse audio**: Upload a custom audio file or choose to reuse the original video's audio.
6. **Start processing**: Click "Generate" to process your video frame-by-frame.
7. **Export**: Download the processed video with audio from the output panel.

### Tips & Troubleshooting 💡

- For best results, use high-quality source videos and clear prompts.
- If you experience flicker, try enabling keyframe compositing and adjusting keyframe intervals.
- Integration with [bg-mask](https://github.com/Scholar01/sd-webui-bg-mask) can improve background consistency.
- For audio, you can provide a separate audio file (WAV/MP3) or reuse the original video's audio track.

---

## 🚀 Advanced Usage Examples

![img1.png](images/1.png)

### Example 1: Keyframe Compositing

- Enable the "Video Editing" tab.
- Choose "Auto-generate keyframes" or manually select keyframes for more control.
- Adjust the keyframe interval to balance between smoothness and processing speed.

### Example 2: Custom Keyframe Selection

- In the "Video Editing" tab, select "Custom Keyframes".
- Mark frames you want as keyframes for style consistency.
- Use the "Backpropel keyframe tag" to propagate styles backward.

### Example 3: Integration with bg-mask

- Install the [bg-mask plugin](https://github.com/Scholar01/sd-webui-bg-mask).
- Enable bg-mask in Mov2mov settings.
- Process your video for improved background masking and less artifacting.

---

## 🎥 Video Tutorials

- [https://www.bilibili.com/video/BV1Mo4y1a7DF](https://www.bilibili.com/video/BV1rY4y1C7Q5](https://www.bilibili.com/video/BV1rY4y1C7Q5)

## 💬 Community

- QQ channel: [https://pd.qq.com/s/akxpjjsgd](https://pd.qq.com/s/akxpjjsgd)
- Discord: [https://discord.gg/hUzF3kQKFW](https://discord.gg/hUzF3kQKFW)

---

## 🙏 Thanks

- modnet-entry: [https://github.com/RimoChan/modnet-entry](https://github.com/RimoChan/modnet-entry)
- MODNet: [https://github.com/ZHKKKe/MODNet](https://github.com/ZHKKKe/MODNet)
- Ezsynth: [https://github.com/Trentonom0r3/Ezsynth](https://github.com/Trentonom0r3/Ezsynth)
