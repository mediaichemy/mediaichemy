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
3. Set up API keys for supported providers (see below).

## AI Providers

### Currently supported providers 


`Text` [**OpenRouter**]()

`Image`: [**Runware**]()

`Video`: [**MiniMax**]()

`Speech`: [**ElevenLabs**]()
<br> 

#### Why we chose these providers
These providers were chosen due to their flexibility, cost-effectiveness, popularity and support. `mediaichemy` is modular, making it easy to add more providers. We plan to expand support for other providers in the future.
### Registration


Before you can start using **mediaichemy**, you need to register and configure API keys for the supported AI providers. Follow these steps:

1. **Create Accounts**:
   - Click the links above to sign up for accounts with each AI providers.

2. **Obtain API Keys**:
   - After registering, obtain API keys from each provider's dashboard.

3. **Configure API Keys**:
   - The recommended way to configure API keys is by setting them as environment variables. For example:
     - `OPENROUTER_API_KEY="your_openrouter_api_key"`
     - `RUNWARE_API_KEY="your_runware_api_key"`
     - `MINIMAX_API_KEY="your_minimax_api_key"`
     - `ELEVENLABS_API_KEY="your_elevenlabs_api_key"`

4. **Alternative: Use `configs.toml`**:
   - If you prefer, you can add the API keys directly to a `configs.toml` file in your working directory in the following format:
     ```toml
     [ai.text.openrouter]
     api_key = "your_openrouter_api_key"

     [ai.image.runware]
     api_key = "your_runware_api_key"

     [ai.video.minimax]
     api_key = "your_minimax_api_key"

     [ai.speech.elevenlabs]
     api_key = "your_elevenlabs_api_key"
     ```

## How to use it

### Single media
The `ai_request` function provides a unified interface for generating individual media types (e.g., text, images, videos, or audio) using AI providers. It abstracts the complexity of interacting with different APIs, allowing you to focus on the content.

#### Example: Generate an AI Image
```python
from mediaichemy.ai.request import ai_request

# Generate an image using a prompt
image = await ai_request(
    media="image",
    prompt="futuristic cityscape, sunset, vibrant colors, high detail",
    output_path="output/image.jpg"
)

print(f"Image saved at: {image.path}")
```
To see more examples
[check the full documentation](https://github.com/your-repo/mediaichemy/wiki)

### Multimedia
The mediaAIChemist class enables seamless workflows for creating complex multimedia content by combining multiple AI-generated media types and applying audio and video edits.

Content can be fully customized by adding configurations to a `configs.toml` in your working directory. You can find multiple configuration examples [here.]()

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