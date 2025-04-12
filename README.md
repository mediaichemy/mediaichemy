# mediaichemy: AI-Powered Multimedia Content Creation

<img src="docs/imgs/mediaichemy.png" min-width="200px" max-width="200px" width="200px" align="right" alt="">

**mediaichemy** is a modular framework designed to simplify the creation of AI-driven multimedia content. It enables users to generate, edit, and combine images, videos, and audio seamlessly. With support for multiple AI providers and customizable workflows, this is the perfect tool for automating AI content creation workflows. 

---

## **Table of Contents**
- [Quickstart](#quickstart)
- [Register](#register)
  - [Supported Providers](#supported-providers)
  - [Setting API Keys](#setting-api-keys)
- [mediAIchemy](#mediaichemy)
  - [General Workflow Example](#general-workflow-example)
  - [How It Works](#how-it-works)
  - [Example Use Case: Short Video Creation](#example-use-case-short-video-creation)
- [ai_request](#ai_request)
  - [Example 1: Generate Text](#example-1-generate-text)
  - [Example 2: Generate an Image](#example-2-generate-an-image)
  - [Example 3: Generate Speech](#example-3-generate-speech)
  - [Example 4: Generate a Video](#example-4-generate-a-video)
- [Configuration](#configuration)
- [Additional Features](#additional-features)
  - [Audio and Video Editing](#audio-and-video-editing)
  - [Idea Generation](#idea-generation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## **Quickstart**

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

4. Start creating content using `mediAIchemy` or `ai_request` (see sections below).

---

## **Register**

To use `mediaichemy`, you need to register with the supported AI providers and set their API keys as environment variables.

### **Supported Providers**

#### **Text Generation**
- [OpenRouter](https://openrouter.ai/)  
  Environment Variable: `OPENROUTER_API_KEY`

#### **Image Generation**
- [Runway](https://runwayml.com/)  
  Environment Variable: `RUNWAY_API_KEY`

#### **Speech Generation**
- [ElevenLabs](https://elevenlabs.io/)  
  Environment Variable: `ELEVENLABS_API_KEY`

#### **Video Generation**
- [MiniMax](https://minimax.com/)  
  Environment Variable: `MINIMAX_API_KEY`

### **Setting API Keys**

Once you have registered with the providers, set the API keys as environment variables. Here’s how to do it:

#### **macOS/Linux**
Add the following lines to your `~/.bashrc` or `~/.zshrc` file:
```bash
export OPENROUTER_API_KEY="your_openrouter_api_key"
export RUNWAY_API_KEY="your_runway_api_key"
export ELEVENLABS_API_KEY="your_elevenlabs_api_key"
export MINIMAX_API_KEY="your_minimax_api_key"
```
Then, reload your shell configuration:
```bash
source ~/.bashrc  # or ~/.zshrc
```

#### **Windows**
Use the `setx` command in the Command Prompt:
```cmd
setx OPENROUTER_API_KEY "your_openrouter_api_key"
setx RUNWAY_API_KEY "your_runway_api_key"
setx ELEVENLABS_API_KEY "your_elevenlabs_api_key"
setx MINIMAX_API_KEY "your_minimax_api_key"
```

After setting the environment variables, restart your terminal or IDE to ensure the changes take effect.

---

## **mediAIchemy**

`mediAIchemy` provides an integrated workflow for creating multimedia content by combining AI services and video/audio editing. It allows users to define workflows that generate and process media in a modular and customizable way.

### **General Workflow Example**

Below is an example of a general workflow using `mediAIchemy`:

```python
import asyncio
from mediaichemy import mediaAIChemist

# Initialize the mediaAIChemist with the desired content type
aichemist = mediaAIChemist(content_type="short_video")

# Generate ideas for content
ideas = await aichemist.generate_ideas()

# Initialize content based on the first idea
content = aichemist.initialize_content(ideas[0])

# Create the content
media = await aichemist.create_content(content)

# Optionally, clean up temporary files
content.purge()
```

### **How It Works**
1. **Generate Ideas**: Use `generate_ideas` to create a list of content ideas based on the configured settings.
2. **Initialize mediaAIChemist**: Create an instance of `mediaAIChemist` with the desired content type (e.g., `short_video`).
3. **Load Content**: Use `initialize_content` to load content details from an idea file.
4. **Generate Media**: Call `create_content` to generate the media using AI services and editing tools.
5. **Clean Up**: Use `purge` to remove temporary files if needed.

### **Example Use Case: Short Video Creation**
The `short_video` content type integrates idea generation, image generation, speech synthesis, and video/audio editing to create short videos. This is just one example of how `mediAIchemy` can be used to streamline multimedia content creation.

For more advanced workflows, you can customize the steps or create your own content types.

---

## **ai_request**

`ai_request` is a unified interface for accessing multiple AI providers to generate specific types of media.

### **Example 1: Generate Text**
```python
from aichemy.ai.request import ai_request

text = asyncio.run(ai_request(
    media="text",
    prompt="Write a motivational quote about life."
))
print(text)
```

### **Example 2: Generate an Image**
```python
from aichemy.ai.request import ai_request

image = asynai_request(
    media="image",
    prompt="A futuristic cityscape at sunset",
    output_path="/path/to/image.jpg"
))
print(f"Image saved at: {image.filepath}")
```

### **Example 3: Generate Speech**
```python
from aichemy.ai.request import ai_request

speech = asyncio.run(ai_request(
    media="speech",
    prompt="Life is a journey, not a destination.",
    output_path="/path/to/speech.mp3"
))
print(f"Speech saved at: {speech.filepath}")
```

### **Example 4: Generate a Video**
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