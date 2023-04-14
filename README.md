# Pax Academia
General purpose utility bot for the Homework Help Discord server



## How to Contribute
1. Fork this repository into your own account.
2. Check out [environment.md](./environment.md) on setting up the environment. 
3. Commit changes to your fork.
4. Open a pull request, making sure to comapre across forks.  
For more information regarding pull requests across forks, please check out GitHub's official docs [here](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork).


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
