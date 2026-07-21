
# Socircle Bot 📋

A simple, asynchronous Telegram bot built with Python (`python-telegram-bot`) and SQLAlchemy. This bot acts as a personal CRM tool to help you keep track of your close circle of friends, including their birthdays, phone numbers, and locations.

---

## 🚀 Features

* **Add Friends:** A step-by-step wizard to save a friend's details.
* **List Friends:** Displays a formatted list of everyone you have saved.
* **Remove Friends:** Generates sleek inline buttons so you can remove a friend with a single click.
* **Smart Cancel:** Safe cancellation handling that lets you back out of any step instantly.

---

## 💻 Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/samousav/circle-managing.git](https://github.com/samousav/circle-managing.git)
cd circle-managing

```

### 2. Configure Your Token

Create a file named `.env` in the root folder and add your Telegram bot token:

```env
BOT_TOKEN=your_telegram_bot_token_here

```

### 3. Run the Bot

```bash
python main.py

```

*(The local SQLite database will automatically configure and create itself on the first run).*

---

## 🤖 Commands

* `/start` - Register and open the persistent main menu.
* `Add` or `/add` - Start the process to add a new friend.
* `List` or `/list` - See your entire circle of friends.
* `Remove` or `/remove` - Choose a friend to delete via inline buttons.
* `Cancel` or `/cancel` - Stop the current action and return to the main menu.

