import reflex as rx
from dashboard.state import UserAppState
from assets.texts_en import items as texts_en
from assets.texts_fa import items as texts_fa


def render_test_user_button(user: dict):
    return rx.button(
        f"Login as {user['name']}",
        on_click=lambda: UserAppState.handle_user_login(user["chat_id"], user["name"]),
        width="100%",
        variant="outline",
        size="3",
        margin_bottom="0.5rem",
    )


def render_mobile_friend_card(friend: dict):
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("user", size=18),
                rx.text(friend["fullname"]),
                rx.text(f"({friend['nickname']})"),
                rx.spacer(),
                rx.hstack(
                    rx.icon_button(
                        rx.icon("pencil", size=16),
                        color_scheme="gray",
                        variant="soft",
                        size="1",
                        radius="full",
                        on_click=lambda: UserAppState.open_edit_friend_drawer(
                            friend["fullname"],
                            friend["nickname"],
                            friend["birthday"],
                            friend["phone"],
                            friend["location"],
                        ),
                    ),
                    rx.icon_button(
                        rx.icon("trash-2", size=16),
                        color_scheme="red",
                        variant="soft",
                        size="1",
                        radius="full",
                        on_click=lambda: UserAppState.prompt_delete_friend(
                            friend["fullname"]
                        ),
                    ),
                    spacing="2",
                ),
                justify="start",
                align="center",
                width="100%",
            ),
            rx.divider(alpha=0.1),
            rx.grid(
                rx.hstack(
                    rx.icon("cake", size=14),
                    rx.text(friend["display_birthday"], size="2"),
                ),
                rx.hstack(
                    rx.icon("phone", size=14), rx.text(friend["phone"], size="2")
                ),
                rx.hstack(
                    rx.icon("map-pin", size=14), rx.text(friend["location"], size="2")
                ),
                columns="1",
                gap="3",
                width="100%",
                padding_top="0.25rem",
                color="rgba(255, 255, 255, 0.66)",
                
            ),
            align_items="start",
            width="100%",
        ),
        box_sizing="border-box",  # Keeps padding inside the 100% boundary
        margin_x="auto",          # Forces perfect horizontal centering
        

        box_shadow="0 15px 35px -5px rgba(0, 0, 0, 0.25)",
        width="100%",
        variant="ghost",
        background_color="rgba(0, 0, 0, 0.25)",
        backdrop_filter="blur(16px)",                  # 3. Blurs out the warm gradient behind it
        border_radius="1.5rem",
        border="1px solid rgba(255, 255, 255, 0.08)",
        padding="1.25rem",
        margin_bottom="0.75rem",
    )


def bottom_navbar():
    return rx.box(
        rx.hstack(
            rx.button(
                rx.icon("plus", size=16),
                UserAppState.texts["add_friend"],
                color_scheme="green",
                flex="1",
                radius="full",
                on_click=lambda: UserAppState.set_show_add_drawer(True),
            ),
            width="100%",
            spacing="3",
        ),
        position="fixed",
        bottom=rx.cond(UserAppState.show_add_drawer, "-8rem", "1.5rem"),
        opacity=rx.cond(UserAppState.show_add_drawer, "0", "1"),
        transition="all 0.4s cubic-bezier(0.32, 0.72, 0, 1)",
        left="0",
        right="0",
        margin="0 auto",
        max_width="30rem",
        width="80%",
        padding="0.66rem",
        background="rgba(0, 0, 0, 0.25)",
        backdrop_filter="blur(16px)",
        border_radius="1.5rem",
        border="1px solid rgba(255, 255, 255, 0.08)",
        box_shadow="0 8px 32px rgba(0, 0, 0, 0.2)",
        z_index="100",
    )
