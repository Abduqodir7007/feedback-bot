# Feedback Bot

Where users can submit their feedback about the service and review their own feedback

## Tech Stack

-   **Python** (Async/Await)
-   **Django ORM** (for database operations)
-   **asgiref** (`sync_to_async` for thread safety)
-   **Telegram Bot API** (via python-telegram-bot)

## Installation

1. git clone https://github.com/yourusername/feedback-bot.git
   cd feedback-bot

2. python -m venv venv
   source venv/bin/activate # macOS/Linux
   venv\Scripts\activate # Windows

3. pip install -r requirements.txt

4. Create your bot via BotFather on Telegram and paste your token to .env file.
