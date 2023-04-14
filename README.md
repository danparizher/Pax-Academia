# Pax Academia
General purpose utility bot for the Homework Help Discord server

## How to Contribute
1. Fork this repository into your own account
2. Commit changes to your fork.
3. Open a pull request, making sure to comapre across forks.
  
Creating a PR across forks: 
![Creating new PR](https://i.imgur.com/DONnpZq.png)

![Comparing across forks ](https://i.imgur.com/huBY6Tx.png)

![Branches on forks](https://i.imgur.com/XBiWFoC.png)


## Environment
1. Clone the forked repository onto your machine.
2. Activate the virtual environment. On windows, running the [`setup.bat`](./setup.bat) file will suffice.  
On Linux/MacOS, create a new virutal environment via
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the required libraries
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

<!-- While the user can't run the exact Pax-Academia bot, this .env file is to configure their bot with the same functionality as Pax-Academia -->
4. Configure the `.env` file.  
    In order to use the functionalities that Pax Academia offers, you will need a `.env` file in the root directory containing the following:

    ```env
    DISCORD_TOKEN = <your discord bot token>
    STAFF_CHANNEL = <the channel ID where new applications are sent>
    ALLOW_SEE_APPS_ROLE = <a role name whose members can see applications>
    MULTIPOST_EMOJI = <optional, specify a custom emoji for multiposts e.g. ":multipost:1046975187930849280">
    ALLOW_MULTIPOST_FOR_ROLE = <a role name whose members are immune to multiposting rules>
    ALLOW_DUMP_DATABASE_GUILD = <a guild ID where the /dump_database command will be enabled>
    ALLOW_DUMP_DATABASE_ROLE = <a role name whose members can use the /dump_database command>
    ```
5. Configure bot permissions.

    You must specify the priveleged gateway intents for the bot through the [application portal](https://discord.com/developers/applications).

    (I, dddictionary, have no clue which intents the bot requires, but enabled all three and it seemed to work. Anyone who knows the intents, please edit this step)

## Before running bot

Before running the bot, you will need to run [`./util/db_builder.py`](./util/db_builder.py):
```bash
python ./util/db_builder.py
```
This file needs to be run once before the bot starts for the first time.

## Running bot

To run the bot, navigate to the root directory and run the following command:
```bash
python main.py
```

You should see the the following text in your terminal:

```txt
<botname> has connected to Discord!
```
where `<botname>` is the name of your bot.