# mediaichemy: AI-Powered Multimedia Content Creation

<img src="docs/imgs/mediaichemy.png" min-width="200px" max-width="200px" width="200px" align="right" alt="">

⚗️🧪🧫 **mediaichemy** is a modular framework designed to simplify the creation of A I-driven multimedia content. It enables users to generate, edit, and combine images, videos, and audio seamlessly. With support for multiple AI providers and customizable workflows, this is the perfect tool for automating AI content creation workflows. 


## Features
🤖 Generate and edit images, videos, and audio using AI.

⚙️ Modular workflows for customizable content creation.

👾 Support for multiple AI providers. 


[`🧪 Check out the full documentation  →`](https://github.com/your-repo/mediaichemy/wiki)


## Examples of Created Content

🚧  🔜
## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/mediaichemy.git
   cd mediaichemy
   ```
2. Install dependencies:
   ```bash
   pip install -e .
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
from mediaichemy import mediaAIChemist

# Initialize mediaAIChemist for short video creation
aichemist = mediaAIChemist(content_type="short_video")

# Generate ideas for the content
ideas = await aichemist.generate_ideas()
print(f"Generated ideas: {ideas}")

# Initialize content based on the first idea
content = aichemist.initialize_content(ideas[0])

# Create the multimedia content
media = await aichemist.create_content(content)
print(f"Multimedia content created: {media}")
```
## Contributing
Contributions are welcome! Check out our [contribution guidelines](https://github.com/your-repo/mediaichemy/wiki/Contributing).


## License
This project is licensed under the MIT License. See the `LICENSE` file for details.