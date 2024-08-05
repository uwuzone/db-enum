import click
import importlib
import os
import json
from datetime import datetime
from typing import Any

from db_enum.logger import VerboseLogger

# Automatically discover DB_TYPES
DB_TYPES = [
    f.split(".")[0]
    for f in os.listdir(os.path.join(os.path.dirname(__file__), "db"))
    if f.endswith(".py") and not f.startswith("__")
]


def custom_json_serializer(obj: Any) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


@click.group()
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """Database enumeration tool for security testing."""
    ctx.ensure_object(dict)
    ctx.obj["logger"] = VerboseLogger(verbose)


@cli.command()
@click.option("--host", required=True, help="Database host")
@click.option("--port", required=True, type=int, help="Database port")
@click.option("--user", required=True, help="Database user")
@click.option("--password", required=True, help="Database password")
@click.option("--database", help="Database name")
@click.pass_context
def magic(ctx, host: str, port: int, user: str, password: str, database: str = None):
    """Automatically detect and enumerate the database type."""
    logger = ctx.obj["logger"]
    for db_type in DB_TYPES:
        module = importlib.import_module(f"db_enum.db.{db_type}")
        if module.check_connection(host, port, user, password, database, logger):
            logger.info(f"Detected {db_type} database. Enumerating...")
            result = module.enumerate(host, port, user, password, database, logger)
            click.echo(json.dumps(result, indent=2, default=custom_json_serializer))
            return
    logger.error("Failed to detect any supported database type.")


# Add subcommands for each database type
for db_type in DB_TYPES:

    @cli.command(name=db_type)
    @click.option("--host", required=True, help="Database host")
    @click.option("--port", required=True, type=int, help="Database port")
    @click.option("--user", required=True, help="Database user")
    @click.option("--password", required=True, help="Database password")
    @click.option("--database", help="Database name")
    @click.pass_context
    def db_command(
        ctx,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str = None,
        db_type: str = db_type,
    ):
        logger = ctx.obj["logger"]
        module = importlib.import_module(f"db_enum.db.{db_type}")
        if module.check_connection(host, port, user, password, database, logger):
            result = module.enumerate(host, port, user, password, database, logger)
            click.echo(json.dumps(result, indent=2, default=custom_json_serializer))
        else:
            logger.error(f"Failed to connect to {db_type} database.")


if __name__ == "__main__":
    cli()
