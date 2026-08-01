import reflex as rx
from dashboard.state import UserAppState

def add_friend_drawer():
    return rx.drawer.root(
        rx.drawer.content(
            rx.form(
                rx.vstack(
                    rx.drawer.handle(),
                    rx.drawer.title(
                        rx.cond(
                            UserAppState.is_editing,
                            UserAppState.texts["edit_drawer_title"],
                            UserAppState.texts["add_drawer_title"],
                        )
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("user", size=16)),
                        placeholder=UserAppState.texts["add_drawer_fullname"],
                        width="100%",
                        text_align="center",
                        radius="full",
                        name="fullname",
                        value=UserAppState.form_fullname,
                        on_change=UserAppState.set_form_fullname,
                        required=True,
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("at-sign", size=16)),
                        placeholder=UserAppState.texts["add_drawer_nickname"],
                        width="100%",
                        text_align="center",
                        radius="full",
                        name="nickname",
                        value=UserAppState.form_nickname,
                        on_change=UserAppState.set_form_nickname,
                        required=True,
                    ),
                    rx.box(
                        rx.hstack(
                            rx.icon("cake", size=16, color_scheme="gray"),
                            rx.text(UserAppState.texts["add_drawer_birthday"], size="2", color_scheme="gray"),
                            rx.spacer(),
                            rx.select(
                                [str(i) for i in range(1, 32)],
                                placeholder=UserAppState.texts["add_drawer_birthday_day"],
                                value=UserAppState.bday_day,
                                on_change=UserAppState.set_bday_day,
                                radius="full",
                                flex="1",
                            ),
                            rx.select(
                                UserAppState.months_list,
                                placeholder=UserAppState.texts["add_drawer_birthday_month"],
                                value=UserAppState.bday_month,
                                on_change=UserAppState.set_bday_month,
                                radius="full",
                                flex="2",
                            ),
                            rx.select(
                                UserAppState.years_list,
                                placeholder=UserAppState.texts["add_drawer_birthday_year"],
                                value=UserAppState.bday_year,
                                on_change=UserAppState.set_bday_year,
                                radius="full",
                                flex="1.5",
                            ),
                            width="100%",
                            align="center",
                            padding_x="0.5rem",
                            padding_bottom="0.5rem",
                        ),
                        color_scheme="gray",
                        radius="full",

                        
                    ),
                    
                    rx.input(
                        rx.input.slot(rx.icon("phone", size=16)),
                        placeholder=UserAppState.texts["add_drawer_phone"],
                        width="100%",
                        text_align="center",
                        radius="full",
                        name="phone",
                        value=UserAppState.form_phone,
                        on_change=UserAppState.set_form_phone,
                        required=True,
                    ),
                    rx.input(
                        rx.input.slot(rx.icon("map-pin", size=16)),
                        placeholder=UserAppState.texts["add_drawer_location"],
                        width="100%",
                        text_align="center",
                        radius="full",
                        name="location",
                        value=UserAppState.form_location,
                        on_change=UserAppState.set_form_location,
                        required=True,
                    ),
                    rx.hstack(
                        rx.button(
                            rx.cond(
                                UserAppState.is_editing,
                                rx.icon("check", size=16),
                                rx.icon("plus", size=16),
                            ),
                            rx.cond(UserAppState.is_editing, UserAppState.texts["save"], UserAppState.texts["add_friend"]),
                            flex="1",
                            width="100%",
                            variant="solid",
                            size="3",
                            radius="full",
                            color_scheme="green",
                            on_click=UserAppState.add_friend,
                        ),
                        rx.drawer.close(
                            rx.button(
                                rx.icon("x", size=16),
                                UserAppState.texts["cancel"],
                                flex="1",
                                width="100%",
                                variant="soft",
                                size="3",
                                radius="full",
                                color_scheme="gray",
                            ),
                        ),
                        width="100%",
                        spacing="4",
                        justify="center",
                        align="center",
                    ),
                    width="100%",
                    max_width="30rem",
                    spacing="4",
                    padding="1rem",
                ),
                on_submit=UserAppState.add_friend,
            ),
            margin="0 auto",
            max_width="30rem",
            width="100%",
            background="rgba(0, 0, 0, 0.5)",
            backdrop_filter="blur(16px) saturate(180%)",
            border_top_left_radius="1.5rem",
            border_top_right_radius="1.5rem",
            height="auto",
            font_family=UserAppState.app_font_family,
        ),
        direction="bottom",
        open=UserAppState.show_add_drawer,
        on_open_change=lambda value: UserAppState.set_show_add_drawer(value),
        
    )


def delete_confirmation_dialog():
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(UserAppState.texts["delete_title"]),
            rx.alert_dialog.description(
                UserAppState.texts["delete_description"].to(str).replace("{fullname}", UserAppState.contact_to_delete),
            ),
            rx.hstack(
                rx.alert_dialog.cancel(
                    rx.button(
                        UserAppState.texts["cancel"],
                        variant="soft",
                        radius="full",
                        color_scheme="gray",
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        UserAppState.texts["delete"], color_scheme="red", on_click=UserAppState.delete_friend, radius="full"
                    )
                ),
                spacing="3",
                justify="end",
                margin_top="1rem",
            ),
            font_family=UserAppState.app_font_family,
        ),
        open=UserAppState.show_delete_dialog,
        on_open_change=lambda value: UserAppState.set_show_delete_dialog(value),
    )
