from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

items = {
    "main_menu": ReplyKeyboardMarkup([["اضافه کردن"], ["لیست افراد"], ["حذف"]], one_time_keyboard=True, resize_keyboard=True),
    "cancel_markup": ReplyKeyboardMarkup([["❌لغو"]], resize_keyboard=True, one_time_keyboard=True),
    "phone_markup": ReplyKeyboardMarkup([["ندارم!"], ["❌ لغو"]], resize_keyboard=True, one_time_keyboard=True),
    
    # Dynamic component helper
    "friend_action_keyboard": lambda fname: InlineKeyboardMarkup([
        [InlineKeyboardButton(text="جداسازی هر فرد", callback_data="view_all_separate")],
        [
            InlineKeyboardButton(text="ویرایش", callback_data=f"edit_target_{fname}"),
            InlineKeyboardButton(text="اضافه کردن", callback_data="inline_add"),
        ],
        [InlineKeyboardButton(text="حذف", callback_data=f"remove_target_{fname}")],
    ]),
    
    "edit_options_keyboard": InlineKeyboardMarkup([
        [InlineKeyboardButton(text="اسم کامل", callback_data="fullname")],
        [
            InlineKeyboardButton(text="لقب", callback_data="nickname"), 
            InlineKeyboardButton(text="تاریخ تولد", callback_data="birthday")
        ],
                [
            InlineKeyboardButton(text="شماره تلفن", callback_data="phone"), 
            InlineKeyboardButton(text="محل زندگی", callback_data="location")
        ]
    ]),
}