import reflex as rx

config = rx.Config(
    app_name="dashboard",
    db_url="sqlite:///../../database.db",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ],
    backend_host="127.0.0.1",
    backend_port=8000,
    frontend_port=3000,
    # If your version of Reflex supports allowed hosts, include your domain:
    # api_url="https://socircle.samousavi.online", 
)