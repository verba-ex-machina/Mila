# Mila
### Mila: The Mindful, Interactive Lifestyle Assistant

## Overview
Mila is a Discord bot designed to interactively assist with lifestyle management using OpenAI's technologies.

"Lifestyle Management" is a broad term that encompasses a variety of activities. What's your lifestyle? Customize Mila to fit your needs.

At the moment, Mila can:

- Search the 'net with DuckDuckGo.
- Retrieve and parse websites.
- Get live weather forecasts via OpenWeatherMap.
- Generate memes via ImgFlip.
- Check your horoscope.
- And more!

Mila can be expanded with additional functionality by adding new tools to `mila/tools/` and registering them in `mila/tools/__init__.py`.

**REMEMBER:** Mila is an experiment. A fun pet project. It is not intended for production use. It connects to your OpenAI key, which is connected to your wallet. Use at your own risk.

## Initial Setup
This guide is intended for macOS/Linux users.

### Cloning the Repository
Clone the Mila repository into a directory of your choice.

```bash
git clone https://github.com/verba-ex-machina/Mila.git
cd Mila
```

### Creating a Virtual Environment
Set up a Python virtual environment in the cloned directory.

```bash
python3 -m venv venv
```

Activate the virtual environment.

```bash
source venv/bin/activate
```

Verify Python path (should be within `venv` directory).

```bash
which python3
```

### Installing Dependencies
Install required dependencies for Mila.

- For general use:
  ```bash
  pip install -r requirements.txt
  ```
- For development:
  ```bash
  pip install -r requirements.txt -r requirements-dev.txt
  ```

### Setting Up API Keys
Obtain and securely store API keys.

1. Get an [OpenAI API key](https://www.google.com/search?q=how+to+find+your+openai+api+key).
2. [Register a Discord bot and get its token](https://www.google.com/search?q=how+to+register+a+new+discord+bot+and+get+its+token).
3. [Add the bot to your server](https://discordjs.guide/preparations/adding-your-bot-to-servers.html#bot-invite-links).
4. Get an [OpenWeatherAPI](https://openweathermap.org/) API key (free with a basic account).
5. Get an [ImgFlip](https://imgflip.com/) account for meme generation.
6. Get a [SerpApi](https://serpapi.com/) API key for search engine results.

### Configuring Environment Variables
Create an `.envrc` file in the root directory with the following content, replacing placeholders with actual API keys.

```bash
export DISCORD_TOKEN="your_discord_token"
export IMGFLIP_USERNAME="your_imgflip_username"
export IMGFLIP_PASSWORD="your_imgflip_password"
export OPENAI_API_KEY="your_openai_api_key"
export OPENWEATHERMAP_API_KEY="your_openweathermap_api_key"
export SERPAPI_API_KEY="your_serpapi_api_key"
layout python3
```

**Important:** Do not commit the `.envrc` file to the repository or share it.

### Loading Environment Variables
There are two ways to load the variables and virtual environment:

- Manually:
  ```bash
  source .envrc
  ```
- Automatically using `direnv` ([installation guide](https://direnv.net/docs/installation.html)).

## Running the Discord Bot (`milabot.py`)
With the setup complete and environment variables loaded, run the `milabot.py` script to activate Mila on Discord.

```bash
./milabot.py
```
