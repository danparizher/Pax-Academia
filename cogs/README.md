# Cogs

Cogs are a way of organizing commands, listeners, and some state into one class. For more information about Cogs, read [the official docs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html).

## Alerts

- Commands implemented:
  - `alerts-add`
  - `alerts-remove`
  - `alerts-list`
- Description:
  - Create alerts for keywords, such as when your name is mentioned.
  - You can add a new alert for a certain keyword, remove a preexisting alert, and list all alerts created.
  - All alerts are stored in the database created by [`/util/db_builder.py`](/util/db_builder.py).

## DeepL

- Commands implemented:
  - `translate`
- Description:
  - Translate between two languages. Currently supports 29 different languages with support for formality.
  - Translation is done asynchronously with two threads.

## DetectAI

- Commands implemented:
  - `detect-ai`
- Description:
  - Reserved for roles with certain permissions.
  - Limited to be used in any channel under a discord category with the name `help` to prevent abuse by users and get the bot banned from copyleaks.
  - Uses selenium to scrape the HTML of the live demo provided by [copyleaks](https://copyleaks.com/) (no api key yet :pensive:).

## Dictionary

- Commands implemented:
  - `define`
- Description:
  - Defines a word provided by user.
  - Uses beautiful soup to web scrape the [Oxford Learned Dictionaries](https://www.oxfordlearnersdictionaries.com) website.
  - Creates a Discord embed with necessary information

## MessageCounter

- Commands implemented:
  - None
- Description:
  - Used to keep track of how many messages a user has sent.
  - Stores the information into the database.
  - The number of messages is used to check for eligibility when applying to become a staff member.

## Misc

- Commands implemented:
  - `ping`
  - `dump-databse`
- Description:
  - Miscellaneous commands to test response time of bot and a dump of the databse for debugging.

## Moderation

- Commands implemented:
  - None
- Description:
  - Is used to detect multiple posts by the same user in different channels.

## PubChem

- Commands implemented:
  - `chemsearch`
- Description:
  - Used to search chemsitry databases for compunds.
  - Creates a Discord embed with necessary information.

## Rules

- Commands implemented:
  - `rule`
- Description:
  - Display a rule as requested by a user.

## StaffAppsBackoffice

- Commands implemented:
  - `see-apps`
- Description:
  - Used by staff memebrs to interact with staff applications.

## StaffAppsUser

- Commands implemented:
  - `apply-for-staff`
- Description:
  - Used by any server member to check staff eligibility and submit an application.

## Surveys

- Commands implemented:
  - None
- Description:
  - A cog to detect if a survey is sent in the wrong channel and alert the message sender to post in the dedicated channel.

## Tips

- Commands implemented:
  - `tip`
- Description:
  - Used to display prewritten tips and ping someone (anonymously or otherwise) to read it.

## Wikipedia

- Commands implemented:
  - `wiki`
- Description:
  - Query wikipedia with a keyword(s) and display a Discord embed with the information.
