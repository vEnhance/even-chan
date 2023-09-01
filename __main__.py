import logging
import os

from dotenv import load_dotenv

from bot import bot

load_dotenv()

logger = logging.getLogger("root")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

if __name__ == "__main__":
    token = os.getenv("EVEN_CHAN_TOKEN")
    assert token is not None
    bot.run(token)
