import app
import click


@click.group()
def main() -> None:
    """CLI entry point"""
    pass


@main.command()
def start_webhook() -> None:
    """Start bot in webhook mode"""
    app.run_webhook()


@main.command()
def start_polling() -> None:
    """Start bot in polling mode"""
    app.run_polling()


if __name__ == "__main__":
    main()
