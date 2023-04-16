# Cogs

Cogs are a way of organizing commands, listeners, and some state into one class. For more information about Cogs, read [the docs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html).

## Alerts

The alerts cog implements the `alerts-add`, `alerts-remove`, and `alerts-list` slash commands. Create alerts for keywords, such as when your name is mentioned.

All alerts are stored in the database created by [`/util/db_builder.py`](/util/db_builder.py). 

## DeepL

The DeepL cog implements the `translate` slash command.

If you're confused as to why there are two different `translate` functions, one is to actually translate the text through the DeepL module while the other one is used to run service in a different thread. Note the use of `async`.

## DetectAI (In Progress)
The DetectAI cog implements the `detect-ai` slash command.

Uses a hacky soltuion to open a browser, submit the text to the form and get the result back. (Correct me if I'm wrong, but this is a WIP).

## Dictionary
The dictionary cog implements the `define` slash command, used to help define certain words. Uses more hacky HTML div element selction stuff to generate a response.

Returns an markdown embed with the definition, and some links to the pronunciation. 

## MessageCounter
The message counter cog does not implement any slash commands but (I assume) is used to keep track of how many messages a user has sent(?).

## Misc
The misc cog implements the `ping` and `dump-database` slash command. 

## Moderation
The moderation cog implements no slash commands but is used to enforce multipost warnings. 

## PubChem
The PubChem cog implements the `chemsearch` slash command, used to search chemsitry databases for compunds.

Builds and embed with compund details and returns an error if compound is not found.

## Rules
The rules cog implements the `rule` slash command used to display the rules. 

## StaffAppsBackoffice
The staff backend to see staff applications. 

## StaffAppsUser
This cog implements the `apply-for-staff` slash command. Users can use this command to check eligibility and submit an application.

## Surveys
A cog to detect if a survey is sent in the wrong channel and alert the message sender to post in the dedicated channel.

## Tips
This cog implements the `tip` slash command to show tips to users.

## Wikipedia
This cog implements the `wiki` slash command to query wikipedia and return the first page from wikipedia. 