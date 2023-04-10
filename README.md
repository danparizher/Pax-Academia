# Pax Academia
General purpose utility bot for the Homework Help Discord server

## environment

To run this bot, you'll need the following .env file in the root directory:

```env
DISCORD_TOKEN = <your discord bot token>
STAFF_CHANNEL = <the channel ID wherenew applications are sent>
ALLOW_SEE_APPS_ROLE = <a role name whose members can see applications>
MULTIPOST_EMOJI = <optional, specify a custom emoji for multiposts e.g. ":multipost:1046975187930849280">
ALLOW_MULTIPOST_FOR_ROLE = <a role name whose members are immune to multiposting rules>
ALLOW_DUMP_DATABASE_GUILD = <a guild ID where the /dump_database command will be enabled>
ALLOW_DUMP_DATABASE_ROLE = <a role name whose members can use the /dump_database command>
```
