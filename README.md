# Mila
Mila: The Mindful, Interactive Lifestyle Assistant

## Getting Started: `milabot.py`
The `milabot.py` script is a demo Discord bot connected to the Mila AI backend. The goal for this script is to provide a PoC interface for interacting with Mila.

To run the script, you'll need an [OpenAI API key](https://www.google.com/search?q=how+to+find+your+openai+api+key), and you'll need to [register a discord bot and get its token](https://www.google.com/search?q=how+to+register+a+new+discord+bot+and+get+its+token), then [add the bot to your server](https://discordjs.guide/preparations/adding-your-bot-to-servers.html#bot-invite-links). The OpenAI API key and Discord Token will need to be saved in an `.envrc` file with contents like so:

```
export DISCORD_TOKEN="{discord token goes here}"
export OPENAI_API_KEY="{openai api key goes here}"
```
_(Omit the {brackets}, of course.)_

**Be sure you never commit your** `.envrc` **file into the repo, nor share it with anyone!** It's in the `.gitignore` for a reason.

The environment variables can be loaded in a couple ways:

* You can run the command `source .envrc` from the root directory of the repo every time you open a new shell, prior to running the bot script.
* You can install `direnv`, and it'll do it automatically. ([Here's a link to the installation guide.](https://direnv.net/docs/installation.html))

With the environment variables loaded, simply run `milabot.py`.