# Cogs

Cogs are a way of organizing commands, listeners, and some state into one class. For more information about Cogs, read [the docs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html).

## Alerts

The alerts cog implements the `alerts-add`, `alerts-remove`, and `alerts-list` slash commands. Create alerts for keywords, such as when your name is mentioned.

All alerts are stored in the database created by [`/util/db_builder.py`](/util/db_builder.py).

## DeepL

The DeepL cog implements the `translate` slash command.

If you're confused as to why there are two different `translate` functions, one is to actually translate the text through the DeepL module while the other one is used to run service in a different thread. Note the use of `async`.

## DetectAI

The DetectAI cog implements the `detect-ai` slash command.

This command is reserved for certain roles, preferrably those with higher authority to use when needed. It is also limited to be used in any channel under a discord category with the name `help`. This is to prevent abuse by users and get the bot banned from copyleaks. 

Uses selenium to scrape the HTML of the live demo provided by copyleaks (no api key yet :pensive:). The bot will find the text field, enter the provided text, find the submit button and click on it. Then it will scrape the website again to find the response and return a discord embed for a user to view.

## Dictionary

The dictionary cog implements the `define` slash command, used to help define certain words. Uses more hacky HTML div element selection stuff to generate a response.

Returns an markdown embed with the definition, and some links to the pronunciation.

## MessageCounter

The message counter cog does not implement any slash commands but is used to keep track of how many messages a user has sent. The message count for a user is used to check eligibility for applying to be a staff member. 

## Misc

The misc cog implements the `ping` and `dump-database` slash command.

## Moderation

The moderation cog implements no slash commands but is used to enforce multipost warnings.

## PubChem

The PubChem cog implements the `chemsearch` slash command, used to search chemsitry databases for compunds.

Builds and embed with compound details and returns an error if compound is not found.

## Rules

The rules cog implements the `rule` slash command used to display the rules.

## StaffAppsBackoffice

The staff backend to see staff applications.

## StaffAppsUser

This cog implements the `apply-for-staff` slash command. Users can use this command to check eligibility and submit an application.

## Surveys

A cog to detect if a survey is sent in the wrong channel and alert the message sender to post in the dedicated channel.

## Tips

This cog implements the `tip` slash command to show tips to users. Users can choose from prewritten tips and ping someone (anonymously or otherwise) to read it.

## Wikipedia

This cog implements the `wiki` slash command to query wikipedia and return the first page from wikipedia.
