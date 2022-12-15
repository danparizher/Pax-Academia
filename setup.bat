Rem !SKA#0001 24/10/2022
Rem This program is used to create and setup the bot and its virtual environment
Rem Only run this program if you have python 3.10 on PATH

Rem create virtual environment
python -m venv venv

Rem activate virtual environment
call venv/Scripts/activate

Rem install requirements
pip install -r requirements.txt

Rem install playwright
playwright install

Rem deactivate virtual environment
deactivate
