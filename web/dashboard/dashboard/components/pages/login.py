import reflex as rx
from web.dashboard.dashboard.components.styles import BASE_PAGE_STYLE as BASE
from dashboard.state import UserAppState


@rx.page(route="/login", title="Socircle | Login")
def login_page() -> rx.Component:
    return rx.center(
        rx.box(
            rx.vstack(
                rx.heading("Hello stranger!", size="8", font_family=BASE.get("font_family", "")),
                rx.text("You can start using Socircle by logging in via Telegram."),
                rx.spacer(),
                
                rx.image(
                    src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Telegram_logo.svg/960px-Telegram_logo.svg.png?_=20220101141644", 
                    width="15%",
                    cursor="pointer",
                    on_click=UserAppState.handle_telegram_click,
                    filter=rx.cond(UserAppState.is_telegram_clicked, "blur(4px)", "none"),
                    transform=rx.cond(UserAppState.is_telegram_clicked, "scale(0.95)", "scale(1)"),
                    transition="all 0.4s ease-in-out",
                ),

                rx.box(
                    rx.box(
                        rx.text("Click the logo to generate a code.", color_scheme="gray"),
                        opacity=rx.cond(UserAppState.is_telegram_clicked, "0", "1"),
                        height=rx.cond(UserAppState.is_telegram_clicked, "0px", "auto"),
                        overflow="hidden",
                        transition="all 0.4s ease-in-out",
                    ),
                    
                    # ... inside your rx.cond for the Code container ...
                    rx.box(
                        rx.vstack(
                            rx.text(f"Your Code: {UserAppState.verification_code}", size="7", weight="bold"),
                            
                            # 🟢 Show Redirect Timer OR Waiting Timer based on state
                            rx.cond(
                                UserAppState.countdown_timer > 0,
                                rx.text(f"Opening Telegram in {UserAppState.countdown_timer}s...", color_scheme="blue"),
                                rx.text(f"Waiting for verification... ({UserAppState.time_to_delete_code}s)", color_scheme="gray"),
                            ),
                            
                            align_items="center",
                        ),
                        opacity=rx.cond(UserAppState.is_telegram_clicked, "1", "0"),
                        height=rx.cond(UserAppState.is_telegram_clicked, "auto", "0px"),
                        overflow="hidden",
                        transition="all 0.4s ease-in-out",
                    ),
                    width="100%",
                    text_align="center",
                ),

                align_items="center",
                spacing="4"
            ),
            # Prevents the main card from snapping if the content height changes
            transition="height 0.4s ease-in-out",
        ),
        **BASE
    )