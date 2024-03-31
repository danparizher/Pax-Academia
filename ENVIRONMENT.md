# Setting up the Environment

1. Clone the forked repository onto your machine.

   - Make sure the default system python version is `>=3.10` as there is a match case within the codebase. Recommended version is `3.11`

2. Create and activate the virtual environment by running the following in your terminal:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required libraries within the virtual environment.

   ```bash
   pip install -r requirements.txt
   ```

<!-- While the user can't run the exact Pax-Academia bot, this .env file is to configure their bot with the same functionality as Pax-Academia -->

4. Configure the `.env` file.  
   In order to use the functionalities that Pax Academia offers, you will need a `.env` file in the root directory containing the following:

   ```env
   DISCORD_TOKEN = <your discord bot token>
   GUILD_ID = <main server ID>
   STAFF_CHANNEL = <the channel ID where new applications are sent>
   STAFF_ROLE = <the role ID for staff members>
   ALLOW_SEE_APPS_ROLE = <a role name whose members can see applications>
   MULTIPOST_EMOJI = <optional, specify a custom emoji for multiposts e.g. ":multipost:1046975187930849280">
   ALLOW_MULTIPOST_FOR_ROLE = <a role name whose members are immune to multiposting rules>
   ALLOW_VIEW_DATABASE_ROLE_NAME = <a role name whose members can use the /view-database command>
   ALLOW_DETECT_AI_ROLE = <a role name whose members can use the /detect-ai command>
   ALLOW_SURVEY_CHANNEL_ID = <the channel ID for where members can post surveys>
   AUTO_FORMAT_CODE_CHANNEL_IDS = <a comma-separated list of channel IDs where code will be auto-formatted>
   DETECT_MEDIA_SPAM_CHANNEL_IDS = <a comma-separated list of channel IDs where media-spam is detected and prevented>
   DEEPL_API_KEY = <your deepl.com api key>
   ALLOW_VIEW_LOGS_ROLE_NAME = <a role name whose members can use the /view-logs command>
   STDOUT_LOG_FILE = <optionally, the file path where stdout is being redirected>
   STDERR_LOG_FILE = <optionally, the file path where stderr is being redirected>
   ```

5. Configure bot permissions.

   You must specify the privileged gateway intents for the bot through the [application portal](https://discord.com/developers/applications).

   The bot requires the `message_content` privileged gateway intent.
