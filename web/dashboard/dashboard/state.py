import reflex as rx
import sys
import sqlalchemy as sa
from pathlib import Path
from datetime import date
from khayyam import JalaliDate

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "database.db"
engine = sa.create_engine(f"sqlite:///{DB_PATH}")
sys.path.insert(0, str(BASE_DIR))

from database import (
    get_friends_from_db,
    add_friend_to_db,
    remove_friend_from_db,
    get_all_users,
    update_friend_info,
    get_user_language,
    set_user_language,
)
from web.dashboard.assets.texts_en import items as texts_en
from web.dashboard.assets.texts_fa import items as texts_fa
from authentication import validate_telegram_data


class UserAppState(rx.State):
    current_chat_id: str = ""
    current_user_name: str = ""
    friends: list[dict] = []
    user_language: str = "fa"
    is_loading: bool = True

    show_add_drawer: bool = False
    form_fullname: str = ""
    form_nickname: str = ""
    form_birthday: str = ""
    form_phone: str = ""
    form_location: str = ""

    is_editing: bool = False
    original_edit_fullname: str = ""
    show_delete_dialog: bool = False
    contact_to_delete: str = ""

    bday_day: str = ""
    bday_month: str = ""
    bday_year: str = ""

    @rx.event
    def fetch_telegram_data(self):
        return rx.call_script(
            "window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp.initData : ''",
            callback=UserAppState.handle_telegram_login,
        )

    @rx.event
    def handle_telegram_login(self, raw_init_data: str):
        if not raw_init_data:
            self.is_loading = False
            return
        
        valid_user = validate_telegram_data(raw_init_data)

        if valid_user:
            self.current_chat_id = str(valid_user.get("id"))
            self.current_user_name = str(valid_user.get("first_name", "User"))
            self.reload_friends()

        else:
            print("🚨 Unauthorized access attempt detected.")

        self.is_loading = False

        if not self.current_chat_id:
            self.is_loading = False
            return

        

    @rx.event
    def change_language(self, language: str):
        self.user_language = language
        set_user_language(self.current_chat_id, language)
        self.reload_friends()

    @rx.event
    def reload_friends(self):
        if not self.current_chat_id:
            return
        
        raw_friends = get_friends_from_db(self.current_chat_id)
        if not raw_friends:
            self.friends = []
            return

        formatted_friends = []
        months = self.texts.get("months", [])

        for friend in raw_friends:
            friends_dict = dict(friend)
            bday = friends_dict.get("birthday", "Not Set")
            
            if bday != "Not Set" and "-" in bday:
                try:
                    gregorian_year, gregorian_month, gregorian_day = map(
                        int, bday.split("-")
                    )
                    gregorian_date = date(
                        gregorian_year, gregorian_month, gregorian_day
                    )

                    if self.user_language == "fa":
                        jalali_date = JalaliDate(gregorian_date)
                        month_name = months[jalali_date.month - 1]
                        friends_dict["display_birthday"] = (
                            f"{jalali_date.day} {month_name} {jalali_date.year}"
                        )
                    else:
                        month_name = months[gregorian_date.month - 1]
                        friends_dict["display_birthday"] = (
                            f"{month_name} {gregorian_date.day}, {gregorian_date.year}"
                        )

                except Exception:
                    friends_dict["display_birthday"] = bday

            else:
                friends_dict["display_birthday"] = bday

            formatted_friends.append(friends_dict)

        self.friends = formatted_friends

    # ================= DRAWER TOGGLES =================
    @rx.event
    def set_show_add_drawer(self, value: bool):
        self.show_add_drawer = value
        if not value:
            self.is_editing = False
            self.original_edit_fullname = ""
            self.form_fullname = ""
            self.form_nickname = ""
            self.form_birthday = ""
            self.form_phone = ""
            self.form_location = ""

            self.bday_year = ""
            self.bday_month = ""
            self.bday_day = ""

    def set_form_fullname(self, value: str):
        self.form_fullname = value

    def set_form_nickname(self, value: str):
        self.form_nickname = value

    def set_form_birthday(self, value: str):
        self.form_birthday = value

    def set_form_phone(self, value: str):
        self.form_phone = value

    def set_form_location(self, value: str):
        self.form_location = value

    def set_bday_day(self, value: str):
        self.bday_day = value

    def set_bday_month(self, value: str):
        self.bday_month = value

    def set_bday_year(self, value: str):
        self.bday_year = value

    # ================= EDIT FRIEND (UNPACKER) =================
    @rx.event
    def open_edit_friend_drawer(
        self, fullname: str, nickname: str, birthday: str, phone: str, location: str
    ):
        self.is_editing = True
        self.original_edit_fullname = fullname
        self.form_fullname = fullname
        self.form_nickname = nickname.replace("(", "").replace(")", "")
        self.form_birthday = birthday
        self.form_phone = phone
        self.form_location = location

        self.bday_year = ""
        self.bday_month = ""
        self.bday_day = ""

        # 🟢 Gregorian DB -> Jalali/English Dropdowns
        if birthday and birthday != "Not Set" and "-" in birthday:
            parts = [p.strip() for p in birthday.split("-")]

            if (
                len(parts) == 3
                and parts[0].isdigit()
                and parts[1].isdigit()
                and parts[2].isdigit()
            ):
                g_year, g_month, g_day = int(parts[0]), int(parts[1]), int(parts[2])
                months_list = self.texts.get("months", [])

                if self.user_language == "fa":
                    g_date = date(g_year, g_month, g_day)
                    j_date = JalaliDate(g_date)

                    self.bday_year = str(j_date.year)
                    self.bday_day = str(j_date.day)
                    if 1 <= j_date.month <= len(months_list):
                        self.bday_month = months_list[j_date.month - 1]
                else:
                    self.bday_year = str(g_year)
                    self.bday_day = str(g_day)
                    if 1 <= g_month <= len(months_list):
                        self.bday_month = months_list[g_month - 1]
            else:
                if len(parts) == 3:
                    self.bday_year, self.bday_month, self.bday_day = parts

        self.show_add_drawer = True

    # ================= COMPUTED VARS =================
    @rx.var
    def months_list(self) -> list[str]:
        return self.texts.get("months", [])

    @rx.var
    def years_list(self) -> list[str]:
        if self.user_language == "fa":
            return [str(i) for i in range(1300, 1406)]
        return [str(i) for i in range(1900, 2027)]

    @rx.var
    def layout_direction(self) -> str:
        return "rtl" if self.user_language == "fa" else "ltr"

    @rx.var
    def texts(self) -> dict:
        if self.user_language == "fa":
            return texts_fa
        return texts_en

    @rx.var
    def app_font_family(self) -> str:
        """Dynamically switch local TTF fonts based on the active language."""
        if self.user_language == "fa":
            return "'CustomFarsi', sans-serif"

        return "'CustomEnglish', sans-serif"

    # ================= ADD FRIEND (PACKER) =================
    @rx.event
    def add_friend(self):
        if not self.current_chat_id:
            return
        if self.bday_year and self.bday_month and self.bday_day:
            months_list = self.texts.get("months", [])
            try:
                month_number = months_list.index(self.bday_month) + 1
                if self.user_language == "fa":
                    j_date = JalaliDate(
                        int(self.bday_year), month_number, int(self.bday_day)
                    )
                    g_date = j_date.todate()
                    self.form_birthday = g_date.strftime("%Y-%m-%d")
                else:
                    self.form_birthday = f"{self.bday_year}-{str(month_number).zfill(2)}-{self.bday_day.zfill(2)}"
            except (ValueError, TypeError):
                self.form_birthday = (
                    f"{self.bday_year}-{self.bday_month}-{self.bday_day}"
                )
        elif not self.is_editing:
            self.form_birthday = "Not Set"

        if (
            not self.form_fullname
            or not self.form_nickname
            or not self.form_birthday
            or not self.form_phone
            or not self.form_location
        ):
            return

        if self.is_editing:
            fields_to_update = {
                "fullname": self.form_fullname,
                "nickname": self.form_nickname,
                "birthday": self.form_birthday,
                "phone": self.form_phone,
                "location": self.form_location,
            }
            for field, value in fields_to_update.items():
                update_friend_info(
                    self.current_chat_id,
                    self.original_edit_fullname,
                    field=field,
                    value=value,
                )
        else:
            add_friend_to_db(
                self.current_chat_id,
                self.form_fullname,
                self.form_nickname,
                self.form_birthday,
                self.form_phone,
                self.form_location,
            )

        self.handle_user_login(self.current_chat_id, self.current_user_name)
        self.set_show_add_drawer(False)  # Re-use the reset function!

    # ================= DELETE FRIEND =================
    @rx.event
    def prompt_delete_friend(self, fullname: str):
        self.show_delete_dialog = True
        self.contact_to_delete = fullname

    @rx.event
    def set_show_delete_dialog(self, value: bool):
        self.show_delete_dialog = value
        if not value:
            self.contact_to_delete = ""

    @rx.event
    def cancel_delete_friend(self):
        self.show_delete_dialog = False
        self.contact_to_delete = ""

    @rx.event
    def delete_friend(self):
        if not self.current_chat_id:
            return

        remove_friend_from_db(self.current_chat_id, self.contact_to_delete)
        self.handle_user_login(self.current_chat_id, self.current_user_name)
        self.show_delete_dialog = False
        self.contact_to_delete = ""
