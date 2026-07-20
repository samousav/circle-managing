from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from khayyam import JalaliDate
import datetime

# ---------- JALALI DATE PICKER ----------


def jalali_year_grid():
    keyboard = []
    current_year = 1375
    for row in range(5):
        row_buttons = [
            InlineKeyboardButton(text=str(y), callback_data=f"DATE-YR-{y}")
            for y in range(current_year, current_year + 4)
        ]
        keyboard.append(row_buttons)
        current_year += 4
    return InlineKeyboardMarkup(keyboard)


def jalali_month_grid(year: int):
    keyboard = []
    months = [
        "فروردین",
        "اردیبهشت",
        "خرداد",
        "تیر",
        "مرداد",
        "شهریور",
        "مهر",
        "آبان",
        "آذر",
        "دی",
        "بهمن",
        "اسفند",
    ]
    current_month = 1
    for row in range(4):
        row_buttons = [
            InlineKeyboardButton(
                text=months[current_month + col - 1],
                callback_data=f"DATE-MO-{year}-{current_month+col}",
            )
            for col in range(3)
        ]
        keyboard.append(row_buttons)
        current_month += 3
    return InlineKeyboardMarkup(keyboard)


def jalali_day_grid(year: int, month: int):
    keyboard = []
    total_days = JalaliDate(year, month, 1).daysinmonth
    current_day = 1
    for row in range(6):
        row_buttons = []
        for col in range(5):
            if current_day <= total_days:
                row_buttons.append(
                    InlineKeyboardButton(
                        text=str(current_day),
                        callback_data=f"DATE-DY-{year}-{month}-{current_day}",
                    )
                )
                current_day += 1
            else:
                row_buttons.append(
                    InlineKeyboardButton(text=" ", callback_data="DATE-IGNORE")
                )
        keyboard.append(row_buttons)
    return InlineKeyboardMarkup(keyboard)


# ---------- GREGORIAN DATE PICKER ----------


def gregorian_year_grid():
    keyboard = []
    current_year = 2000
    for row in range(5):
        row_buttons = [
            InlineKeyboardButton(text=str(y), callback_data=f"DATE-YR-{y}")
            for y in range(current_year, current_year + 4)
        ]
        keyboard.append(row_buttons)
        current_year += 4
    return InlineKeyboardMarkup(keyboard)




def gregorian_month_grid(year: int):
    keyboard = []
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    current_month = 1
    for row in range(4):
        row_buttons = [InlineKeyboardButton(text=months[current_month+col-1], callback_data=f"DATE-MO-{year}-{current_month+col}") for col in range(3)]
        keyboard.append(row_buttons)
        current_month += 3
    return InlineKeyboardMarkup(keyboard)


def get_days_in_month(year, month) -> int:
    if month in [4, 6, 9, 11]:
        return 30
    elif month == 2:
        is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        return 29 if is_leap else 28
    return 31


def gregorian_day_grid(year: int, month: int):
    keyboard = []
    total_days = get_days_in_month(year, month)
    current_day = 1
    for row in range(6):
        row_buttons = []
        for col in range(5):
            if current_day <= total_days:
                row_buttons.append(InlineKeyboardButton(text=str(current_day), callback_data=f"DATE-DY-{year}-{month}-{current_day}"))
                current_day += 1
            else:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="DATE-IGNORE"))
        keyboard.append(row_buttons)
    return InlineKeyboardMarkup(keyboard)




def format_birthday_for_user(birthday, user_lang):
    if not birthday or birthday == "N/A":
        return "N/A" if user_lang == "en" else "ثبت نشده"
    
    try:
        day, month, year = map(int, birthday.split())
        greg_date = datetime.date(year, month, day)

        if user_lang == "fa":
            jalali_date = JalaliDate(greg_date)
            return f"{jalali_date.day} {jalali_date.monthname()} {jalali_date.year}"
        else:
            return greg_date.strftime("%d %m %Y")
        
    except Exception:
        return "ERROOOOOORRRR!!!!!!!!!"