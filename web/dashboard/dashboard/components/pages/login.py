import reflex as rx
from web.dashboard.dashboard.components.styles import BASE_PAGE_STYLE as BASE
from dashboard.state import UserAppState



def login_page() -> rx.Component:
    return rx.center(
        rx.box(
            rx.vstack(
                rx.heading("Hello stranger!", size="8", font_family=BASE["font_family"]),
                rx.text("You can start using Socircle by logging in via Telegram."),
                rx.spacer(),
                rx.cond(UserAppState.is_telegram_clicked,
                        rx.vstack(
                            rx.text(UserAppState.verification_code, size="8", weight="bold"),
                            rx.text("Send this code to the bot in Telegram to verify your account.", size="2"),
                            rx.text(f"You'll be redirected to the Telegram bot in {UserAppState.countdown_timer} seconds.", size="2"),
                            rx.spacer(),
                            align_items="center",
                            justify="center"
                        )),
                rx.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/960px-Telegram_logo.svg.png?_=20220101141644", width="15%",
                         on_click=UserAppState.handle_telegram_click,
                         cursor="pointer",
                         filter=rx.cond(UserAppState.is_telegram_clicked, "blur(25px)", "none"),
                         transition="filter 0.3s ease-in-out"
                         ),
                align_items="center",
                spacing="4"
            )
        ),
        **BASE
    )