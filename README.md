# mediaichemy: AI-Powered Multimedia Content Creation


<img src="docs/imgs/mediaichemy.png" min-width="200px" max-width="200px" width="210px" align="right" alt="">

**mediaichemy** is a modular framework designed to simplify the creation of AI-driven multimedia content. It enables users to generate, edit, and combine images, videos, and audio seamlessly. With support for multiple AI providers and customizable workflows, MediaiChemy is the perfect tool for creating engaging short video content. 

---

## **Features**
- **AI-Powered Media Generation**: Generate images, videos, and speech using AI providers.
- **Audio and Video Editing**: Seamlessly edit and combine audio and video files.
- **Customizable Workflows**: Configure behavior through a `configs.toml` file.
- **Support for Multiple Languages**: Generate speech in different languages.
- **Idea Generation**: Automatically generate creative ideas for your content.

---

## **Installation**

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/mediaichemy.git
   cd mediaichemy
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure `ffmpeg` is installed on your system:
   ```bash
   # macOS
   brew install ffmpeg

   # Linux
   sudo apt install ffmpeg

   # Windows
   choco install ffmpeg
   ```

---

## **Using `ai_request`**

The `ai_request` function is a unified interface for generating media using AI providers. It supports multiple media types, including `text`, `image`, `video`, and `speech`.

### **Example 1: Generate Text**
To generate text, configure the `configs.toml` file as follows:
```toml
[ai.text.openrouter]
provider = "openrouter"
api_key = "your_openrouter_api_key"
```

Then, use the following code:
```python
from aichemy.ai.request import ai_request

text = asyncio.run(ai_request(
    media="text",
    prompt="Write a motivational quote about life."
))
print(text)
```

---

### **Example 2: Generate an Image**
To generate an image, configure the `configs.toml` file:
```toml
[ai.image.runware]
provider = "runware"
api_key = "your_runware_api_key"
```

Then, use the following code:
```python
from aichemy.ai.request import ai_request

image = asyncio.run(ai_request(
    media="image",
    prompt="A futuristic cityscape at sunset",
    output_path="/path/to/image.jpg"
))
print(f"Image saved at: {image.filepath}")
```

---

### **Example 3: Generate Speech**
To generate speech, configure the `configs.toml` file:
```toml
[ai.speech.elevenlabs]
provider = "elevenlabs"
api_key = "your_elevenlabs_api_key"
voice_settings.speed = 1.2
```

Then, use the following code:
```python
from aichemy.ai.request import ai_request

speech = asyncio.run(ai_request(
    media="speech",
    prompt="Life is a journey, not a destination.",
    output_path="/path/to/speech.mp3"
))
print(f"Speech saved at: {speech.filepath}")
```

---

### **Example 4: Generate a Video**
To generate a video, configure the `configs.toml` file:
```toml
[ai.video.minimax]
provider = "minimax"
api_key = "your_minimax_api_key"
```

Then, use the following code:
```python
from aichemy.ai.request import ai_request

video = asyncio.run(ai_request(
    media="video",
    prompt="A futuristic cityscape at sunset",
    output_path="/path/to/video.mp4"
))
print(f"Video saved at: {video.filepath}")
```

---

## **Short Video Workflow**

The `ShortVideoCreator` class provides a complete workflow for generating short video content. Below is an example workflow:

### **Example Workflow**
```python
import asyncio
from aichemy.content.short_video.short_video_creator import ShortVideoCreator
from aichemy.content.short_video.short_video import ShortVideo

# Initialize the ShortVideoCreator
creator = ShortVideoCreator()

# Define the content details
content = ShortVideo(
    dir="/path/to/output",  # Directory to save the generated content
    image_prompt="A futuristic cityscape at sunset",  # Image prompt
    texts={"en": "Life is a journey, not a destination."},  # Texts for speech
    languages=["en"]  # Languages for the speech
)

# Create the short video content
asyncio.run(creator.create(content))
```

### **What Happens?**
1. **Image Generation**: An image is generated based on the `image_prompt`.
2. **Video Creation**: A video is created using the generated image.
3. **Speech Generation**: Speech is generated for the provided text in the specified language(s).
4. **Video Editing**: The video is extended to match the duration of the speech.
5. **Audio Editing**: Background audio is added to the speech.

---

## **Configuration**

The framework uses a `configs.toml` file to manage settings for AI providers and other features.

### **Example Configuration**
```toml
[content.shortvideo]
n_ideas = 1
languages = ["en"]
text_details = "Deep, but absolutely random, short text about life"
img_tags = "Amazing, futuristic, cityscape, sunset"
extend_method = "ai"

[ai.text.openrouter]
provider = "openrouter"
api_key = "your_openrouter_api_key"

[ai.image.runware]
provider = "runware"
api_key = "your_runware_api_key"

[ai.speech.elevenlabs]
provider = "elevenlabs"
api_key = "your_elevenlabs_api_key"
voice_settings.speed = 1.2

[ai.video.minimax]
provider = "minimax"
api_key = "your_minimax_api_key"
```

---

## **Additional Features**

### **Audio and Video Editing**
The framework includes tools for editing audio and video files:
- **Extend Video Duration**: Extend a video to match a specific duration.
- **Mix Audio Files**: Combine two audio files with adjustable relative volumes.
- **Add Background Audio**: Add background music to a speech file.

### **Idea Generation**
Use the `generate_ideas` method in `ShortVideoCreator` to generate content ideas:
```python
ideas = asyncio.run(creator.generate_ideas())
print(ideas)
```

---

## **Troubleshooting**
- **FFmpeg Not Found**: Ensure FFmpeg is installed and added to your system's PATH.
- **Missing Dependencies**: Run `pip install -r requirements.txt` to install all required libraries.
- **Permission Errors**: Ensure you have write permissions for the output directory.

---

## **Contributing**
Contributions are welcome! Feel free to open issues or submit pull requests.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.