import reflex as rx

config = rx.Config(
    app_name="dashboard",
    db_url="sqlite:///../../database.db",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)