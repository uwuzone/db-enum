import importlib
import os
import json
import signal

from datetime import datetime
from typing import Any
from contextlib import contextmanager

import click

from .logger import VerboseLogger


def custom_json_serializer(obj: Any) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    # raise TypeError(f"Type {type(obj)} not serializable")
    return str(obj)


# Automatically discover DB_TYPES
DB_TYPES = [
    f.split(".")[0]
    for f in os.listdir(os.path.join(os.path.dirname(__file__), "db"))
    if f.endswith(".py") and not f.startswith("__")
]


class TimeoutError(Exception):
    pass


@contextmanager
def fail_on_timeout(seconds):
    def signal_handler(signum, frame):
        raise TimeoutError("Timed out!")

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)


def check_connection_with_timeout(
    module,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    logger: VerboseLogger,
    timeout_seconds: int = 5,
) -> bool:
    try:
        with fail_on_timeout(timeout_seconds):
            return module.check_connection(host, port, user, password, database, logger)
    except TimeoutError:
        logger.error(
            f"Connection to {module.get_info()['name']} at {host}:{port} timed out after {timeout_seconds} seconds"
        )
        return False
    except Exception as e:
        logger.error(
            f"Error connecting to {module.get_info()['name']} at {host}:{port}: {str(e)}"
        )
        return False


@click.group()
@click.option("--verbose", is_flag=True, help="Enable verbose output")
@click.option(
    "--global-timeout",
    default=60,
    help="Global timeout for the entire command execution in seconds",
)
@click.pass_context
def cli(ctx, verbose, global_timeout):
    """Database enumeration tool for security testing."""
    ctx.ensure_object(dict)
    ctx.obj["logger"] = VerboseLogger(verbose)
    ctx.obj["global_timeout"] = global_timeout


@cli.command()
@click.option("--host", required=True, help="Database host")
@click.option("--port", required=True, type=int, help="Database port")
@click.option("--user", required=False, help="Database user")
@click.option("--password", required=False, help="Database password")
@click.option("--database", help="Database name")
@click.option("--timeout", default=15, help="Connection timeout in seconds")
@click.pass_context
def magic(
    ctx, host: str, port: int, user: str, password: str, database: str, timeout: int
):
    """Automatically detect and enumerate the database type."""
    logger = ctx.obj["logger"]
    global_timeout = ctx.obj["global_timeout"]
    logger.info(
        f"Auto-detecting database type, {timeout}s limit per detection. This can take a while..."
    )

    try:
        with fail_on_timeout(global_timeout):
            for db_type in DB_TYPES:
                logger.info(f"Trying to connect with {db_type} client...")
                module = importlib.import_module(f"db_enum.db.{db_type}")
                if check_connection_with_timeout(
                    module, host, port, user, password, database, logger, timeout
                ):
                    logger.info(f"Detected {db_type} database. Enumerating...")
                    result = module.enumerate(
                        host, port, user, password, database, logger
                    )
                    click.echo(
                        json.dumps(result, indent=2, default=custom_json_serializer)
                    )
                    return
            logger.error("Failed to detect any supported database type.")
            exit(1)
    except TimeoutError:
        logger.error(
            f"Global timeout of {global_timeout} seconds reached. Operation aborted."
        )
        exit(1)


# Modify the individual database commands as well
for db_type in DB_TYPES:

    @cli.command(name=db_type)
    @click.option("--host", required=True, help="Database host")
    @click.option("--port", required=True, type=int, help="Database port")
    @click.option("--user", required=False, help="Database user")
    @click.option("--password", required=False, help="Database password")
    @click.option("--database", help="Database name")
    @click.option("--timeout", default=15, help="Connection timeout in seconds")
    @click.pass_context
    def db_command(
        ctx,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        timeout: int,
        db_type: str = db_type,
    ):
        logger = ctx.obj["logger"]
        global_timeout = ctx.obj["global_timeout"]

        try:
            with fail_on_timeout(global_timeout):
                module = importlib.import_module(f"db_enum.db.{db_type}")
                if check_connection_with_timeout(
                    module, host, port, user, password, database, logger, timeout
                ):
                    result = module.enumerate(
                        host, port, user, password, database, logger
                    )
                    click.echo(
                        json.dumps(result, indent=2, default=custom_json_serializer)
                    )
                else:
                    logger.error(f"Failed to connect to {db_type} database.")
                    exit(1)
        except TimeoutError:
            logger.error(
                f"Global timeout of {global_timeout} seconds reached. Operation aborted."
            )
            exit(1)


if __name__ == "__main__":
    cli()
