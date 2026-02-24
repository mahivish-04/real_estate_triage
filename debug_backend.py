import traceback

from backend.app import app
from backend.config import API_HOST, API_PORT


def main() -> None:
    """Run Uvicorn server and log any startup errors to debug_backend.log."""
    import uvicorn

    with open("debug_backend.log", "w", encoding="utf-8") as f:
        try:
            f.write("starting backend debug runner\n")
            f.flush()
            uvicorn.run(app, host=API_HOST, port=API_PORT, reload=False)
        except Exception as exc:  # pragma: no cover - debug path
            f.write("exception during uvicorn.run\n")
            traceback.print_exc(file=f)
            f.write(f"\nERROR: {exc!r}\n")
            f.flush()


if __name__ == "__main__":
    main()

