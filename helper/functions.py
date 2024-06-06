# Import necessary modules
from datetime import datetime
import json
import os




# Define a function to convert seconds to (hours, minutes and seconds)
def eta_converter(seconds: int) -> tuple:
    """
    Converts the given number of seconds into days, hours, minutes, and seconds.

    Args:
        seconds (int): The number of seconds to convert.

    Returns:
        tuple: A tuple containing the number of days, hours, minutes, and seconds.
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return days, hours, minutes, seconds


# Define a function to handle JSON input/output operations
def json_io(mode=None, infos: dict=None, name='infos.json') -> dict:
    """
    Handles JSON input/output operations.

    Args:
        mode (str, optional): The mode of operation. Can be 'w' for write or 'r' for read.
        infos (dict, optional): The dictionary to write to the JSON file.
        name (str, optional): The name of the JSON file.

    Returns:
        dict: The dictionary read from the JSON file if mode is 'r'.
    """
    if mode == 'w':
        with open(name, "w") as f:
            json.dump(infos, f, indent=3)
    elif os.path.exists(name) and mode == 'r':
        with open(name, "r") as f:
            return json.load(f)
        

async def unauthorized(message):
    msg = 'Hahaha, got you 😂😂\n'
    msg += 'Chedk out my repo and host your own bot on your local maching at no cost.\n'
    msg += '**[Spam Bot Repo](https://github.com/shadoworbs/spam_bot)**\n'
    msg += "Don't forget to fort and star the repo."
    await message.reply(msg)


