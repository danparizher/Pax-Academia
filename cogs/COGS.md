# Cogs

Cogs are a way of organizing commands, listeners, and some state into one class. For more information about Cogs, read [the docs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html).

## Alerts

The alerts cog implements the `alerts-add`, `alerts-remove`, and `alerts-list` slash commands.

All alerts are stored in the database created by [`/util/db_builder.py`](/util/db_builder.py). 

## DeepL

The DeepL cog implements the `translate` slash command.

If you're confused as to why there are two different `translate` functions, one is to actually translate the text through the DeepL module while the other one is used to run service in a different thread. Note the use of `async`.

## Detect AI
The DetectAI cog implements the `detect-ai` slash command.

Uses a hacky soltuion to open a browser, submit the text to the form and get the result back. (Correct me if I'm wrong, but this is a WIP).

