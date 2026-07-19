from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

items = {
    "main_menu": ReplyKeyboardMarkup(
        [["Add"], ["List of Friends"], ["Remove"]],
        one_time_keyboard=True,
        resize_keyboard=True,
    ),
    "cancel_markup": ReplyKeyboardMarkup(
        [["❌Cancel"]], resize_keyboard=True, one_time_keyboard=True
    ),
    "phone_markup": ReplyKeyboardMarkup(
        [["I don't have it"], ["❌ Cancel"]],
        resize_keyboard=True,
        one_time_keyboard=True,
    ),
    # Dynamic component helper
    "friend_action_keyboard": lambda fname: InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Show separately", callback_data="view_all_separate"
                )
            ],
            [
                InlineKeyboardButton(text="Edit", callback_data=f"edit_target_{fname}"),
                InlineKeyboardButton(text="Add", callback_data="inline_add"),
            ],
            [
                InlineKeyboardButton(
                    text="Delete", callback_data=f"remove_target_{fname}"
                )
            ],
        ]
    ),
    "edit_options_keyboard": InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="Fullname", callback_data="fullname")],
            [
                InlineKeyboardButton(text="Nickname", callback_data="nickname"),
                InlineKeyboardButton(text="Birthday", callback_data="birthday"),
            ],
            [
                InlineKeyboardButton(text="Phone", callback_data="phone"),
                InlineKeyboardButton(text="Location", callback_data="location"),
            ],
        ]
    ),
}
