import click

from elsa_telegram_bot import app


@click.group()
def main() -> None:
    """CLI entry point"""
    pass


@main.command()
def start() -> None:
    """Start bot"""
    app.run()


if __name__ == "__main__":
    main()
