"""Start the TrustScore backend (FastAPI) and the desktop frontend (Flet) together."""
import threading
import time

import httpx
import uvicorn

from app.config.settings import settings


def start_api():
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, log_level="info")


if __name__ == "__main__":
    threading.Thread(target=start_api, daemon=True).start()
    for _ in range(60):  # wait until the API answers (model/DB init can take a moment)
        try:
            if httpx.get(f"http://{settings.api_host}:{settings.api_port}/health", timeout=1).status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    import flet as ft
    from app.frontend.app import ASSET_DIR, main
    ft.run(main, assets_dir=str(ASSET_DIR))
