import reflex as rx
from dashboard.state import UserAppState
from dashboard.components.navigation import bottom_navbar, render_test_user_button, render_mobile_friend_card
from dashboard.components.overlays import add_friend_drawer, delete_confirmation_dialog
from web.dashboard.dashboard.components.styles import BASE_PAGE_STYLE


def index() -> rx.Component:
    return rx.box(
        rx.cond(
            UserAppState.is_loading,
            # --- THE LOADING SPINNER ---
            rx.center(rx.spinner(size="3"), align="center",justify="center", width="100%", height="100vh"),
            # --- THE LOGGED-IN UI ---
            rx.vstack(
                # 🟢 THE HEADER ROW (Horizontal Stack)
                rx.hstack(
                    rx.vstack(
                        rx.heading(UserAppState.texts["hello"].to(str).replace("{firstname}", UserAppState.current_user_name), size="6", font_family=UserAppState.app_font_family),
                        rx.text(
                            UserAppState.texts["number_of_friends"].to(str).replace("{friends_count}", UserAppState.friends.length().to(str)),
                            color_scheme="gray"
                        ),
                        align_items="start",
                        spacing="1",
                    ),
                    rx.spacer(), 
                    
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.icon_button(
                                rx.icon("settings", size=20),
                                variant="ghost",
                                color_scheme="gray",
                                radius="full",
                                size="2",
                            )
                        ),
                        rx.popover.content(
                            rx.flex(
                                rx.text(UserAppState.texts["settings"], size="2", weight="bold", margin_bottom="0.5rem", font_family=UserAppState.app_font_family),
                                rx.text(UserAppState.texts["language"], size="1", color_scheme="gray", margin_bottom="0.5rem", font_family=UserAppState.app_font_family),
                                rx.select(
                                    ["en", "fa"], 
                                    placeholder="Select a language", 
                                    value=UserAppState.user_language, 
                                    on_change=UserAppState.change_language,
                                    variant="soft",
                                    color_scheme="gray",
                                    width="100%", 
                                    margin_top="0.25rem"
                                ),
                                direction="column",
                            ),
                            width="10rem",
                            font_family=UserAppState.app_font_family,
                            background_color="rgba(0, 0, 0, 0.45)",         # Slightly darker than the cards
                            backdrop_filter="blur(24px)",                   # Heavy blur
                            border="1px solid rgba(255, 255, 255, 0.1)",    # Light-catching edge
                            border_radius="1rem",                           # Soft rounded corners
                            box_shadow="0 20px 40px -5px rgba(0, 0, 0, 0.5)"
                        )
                    ),
                    width="100%",
                    align_items="center", 
                    padding_y="1rem",

                ),
                
                rx.cond(
                    UserAppState.friends.length() > 0,
                    rx.vstack(
                        rx.foreach(UserAppState.friends, render_mobile_friend_card),
                        width="100%",
                        padding_bottom="8rem",
                    ),
                    rx.center(
                        rx.text("No friends found.", color_scheme="gray"),
                        padding_y="4rem",
                    ),
                ),
                width="100%",
            ),
            
        ),  
        # --- RENDER NAVBAR (Animation handles the rest) ---
        rx.cond(
            UserAppState.current_chat_id != "",
            bottom_navbar(),
        ),
        rx.cond(
            rx.State.is_hydrated,
            add_friend_drawer(),
        ),
        rx.cond(
            rx.State.is_hydrated,
            delete_confirmation_dialog(),
        ),
        **BASE_PAGE_STYLE,
    )
