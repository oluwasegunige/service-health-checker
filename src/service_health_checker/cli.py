import typer

from .health_check import health_check

app = typer.Typer()
app.command()(health_check)

if __name__ == "__main__":
    app()