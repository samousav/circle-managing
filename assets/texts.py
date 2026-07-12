from telegram import ReplyKeyboardMarkup

start_command_text = """Hello {first_name} I'm a bot that helps you manage your social circle.
Tap /help or if you know how to use the bot, start with the buttons below."""

keyboard = [
        ["Add"],
        ["List of Friends"],
        ["Remove"]
    ]

main_menu = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
cancel_markup = ReplyKeyboardMarkup(
    [["❌Cancel"]], 
    resize_keyboard=True, 
    one_time_keyboard=True
)

help_text = """Thank you for choosing me! Here are the commands you can use:

- Add a friend /add
- List of friends /list
- Remove a friend /remove
- Edit a friends info /edit"""

friend_added_text = """Great! You added a new friend! It's {fullname}, they're called {nickname}, they're born in {birthday}. Their phone number is {phone} and they live in {location}."""

cancel_text = "Okay, I won't add your new friend. :(. You can add a new friend by tapping /add again, whenever you liked."

list_of_friends_text = """
╭ 👤 Fullname: {fullname}
┊ 💬 Nickname: {nickname}
┊ 🥳 Birthday: {birthday}
┊ 📞 Phone Number: {phone}
╰ 📍 Location: {location}
"""