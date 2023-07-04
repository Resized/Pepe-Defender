# Discord Bot

This project is a Discord bot that allows users to play sound clips in voice channels. It provides utility functions and commands for playing and managing sound clips.

## Features

- Play sound clips in voice channels
- Search for sound clips by name
- Specify volume level for sound clips

## Prerequisites

- Python 3.6 or higher
- discord.py library
- ffmpeg library
- dotenv library

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/your-username/discord-bot-sound-player.git
   ```

2. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory and add your Discord bot token:

   ```plaintext
   DISCORD_TOKEN=your-bot-token
   ```

## Usage

1. Add sound clips to the `sounds/` directory. The bot supports MP3 format.

2. Start the bot by running the following command:

   ```shell
   python bot.py
   ```

3. Invite the bot to your Discord server and make sure it has the necessary permissions to join voice channels.

4. Use the following commands to interact with the bot:

   - `!play <clip>`: Play a sound clip in the current voice channel.
   - `!search <clip>`: Search for sound clips by name.
   - `!volume <level>`: Set the volume level for sound clips (0.0 to 1.0).
