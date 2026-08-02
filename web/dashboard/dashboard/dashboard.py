import reflex as rx
import sqlalchemy as sa
from pathlib import Path
from dashboard.components.pages.index import index
from dashboard.state import UserAppState

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / "database.db"

engine = sa.create_engine(f"sqlite:///{DB_PATH}")


app = rx.App(
    stylesheets=[
        "/styles.css",
    ],
    head_components=[
        rx.script(
            src="https://telegram.org/js/telegram-web-app.js",
            strategy="beforeInteractive",
        )
    ],
)

app.add_page(index, route="/", on_load=UserAppState.fetch_telegram_data)
