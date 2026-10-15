"""The demo site: a stand-in for the application that embeds the chat.

A real host application is a shop, an intranet, a blog. This one is three placeholder pages
that later steps fill in: a public shop, and an intranet seen by two users who belong to
different groups. It never imports the gateway's code - the host application and the gateway
only ever talk over HTTP.
"""

from html import escape

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

PAGES = {
    "/": (
        "Demo shop",
        "A public page. Anyone may chat here, and is answered from documents labelled public.",
    ),
    "/intranet/hr": (
        "Intranet - HR user",
        "A page for logged-in staff, here as a user in the hr group.",
    ),
    "/intranet/engineering": (
        "Intranet - engineering user",
        "A page for logged-in staff, here as a user in the engineering group.",
    ),
}
NAVIGATION = [
    ("/", "Shop"),
    ("/intranet/hr", "Intranet (hr)"),
    ("/intranet/engineering", "Intranet (engineering)"),
]


def _page(title: str, description: str) -> str:
    links = " | ".join(f'<a href="{path}">{escape(label)}</a>' for path, label in NAVIGATION)
    return (
        "<!doctype html>\n"
        f'<html lang="en"><head><meta charset="utf-8"><title>{escape(title)}</title></head>\n'
        f"<body><nav>{links}</nav><h1>{escape(title)}</h1><p>{escape(description)}</p>\n"
        "<p><em>The chat widget will appear on this page.</em></p></body></html>\n"
    )


def create_app() -> FastAPI:
    app = FastAPI(title="ragbridge-chat demo site", docs_url=None, openapi_url=None)

    for path, (title, description) in PAGES.items():
        # The default arguments bind this page's values: a closure over the loop variables
        # would give every route the last page.
        def render(title: str = title, description: str = description) -> HTMLResponse:
            return HTMLResponse(_page(title, description))

        app.add_api_route(path, render, methods=["GET"], response_class=HTMLResponse)
    return app


app = create_app()
