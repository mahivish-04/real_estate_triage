import traceback


def main() -> None:
    """Debug import for backend.app, writing any errors to debug_backend_import.log."""
    with open("debug_backend_import.log", "w", encoding="utf-8") as f:
        try:
            import backend.app as app  # noqa: F401

            f.write("backend.app import OK\n")
            f.flush()
        except Exception as exc:  # pragma: no cover - debug path
            f.write("exception during import backend.app\n")
            traceback.print_exc(file=f)
            f.write(f"\nERROR: {exc!r}\n")
            f.flush()


if __name__ == "__main__":
    main()

