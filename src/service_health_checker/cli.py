import typer

from .health_check import healthcheck

app = typer.Typer()
app.command()(healthcheck)

if __name__ == "__main__":
    app()