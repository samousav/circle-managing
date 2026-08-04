import reflex as rx
from dashboard.state import UserAppState


BASE_PAGE_STYLE = {
    "on_mount": UserAppState.fetch_telegram_data,
    "dir": UserAppState.layout_direction,
    "font_family": UserAppState.app_font_family,
    "background": "linear-gradient(180deg, #FE7E3C 0%, #E4201B 100%)",
    "background_attachment": "fixed",
    "margin": "0 auto",
    "padding": "1rem",
    "max_width": "30rem",
    "min_height": "100vh",
    "position": "relative",
}