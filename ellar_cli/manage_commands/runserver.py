from __future__ import annotations

import ssl
import typing as t
from datetime import datetime

from ellar import __version__ as ellar_version
from ellar.utils.enums import create_enums_from_list
from uvicorn import config as uvicorn_config
from uvicorn import run as uvicorn_run
from uvicorn.config import (
    HTTP_PROTOCOLS,
    INTERFACES,
    LIFESPAN,
    LOG_LEVELS,
    LOGGING_CONFIG,
    LOOP_SETUPS,
    SSL_PROTOCOL_VERSION,
    WS_PROTOCOLS,
)

import ellar_cli.click as eClick
from ellar_cli.constants import ELLAR_META
from ellar_cli.service import EllarCLIException, EllarCLIService

__all__ = ["runserver"]

_LOG_LEVELS = dict(**LOG_LEVELS, NOT_SET=0)
LOG_LEVELS_CHOICES = create_enums_from_list("LOG_LEVELS", *list(_LOG_LEVELS.keys()))

LEVEL_CHOICES = eClick.Choice(list(LOG_LEVELS.keys()))
HTTP_CHOICES = eClick.Choice(list(HTTP_PROTOCOLS.keys()))
WS_CHOICES = eClick.Choice(list(WS_PROTOCOLS.keys()))

LIFESPAN_CHOICES = eClick.Choice(list(LIFESPAN.keys()))
LOOP_CHOICES = eClick.Choice([key for key in LOOP_SETUPS.keys() if key != "none"])
INTERFACE_CHOICES = eClick.Choice(INTERFACES)


@eClick.option(
    "--host",
    type=str,
    default="127.0.0.1",
    help="Bind socket to this host.",
    show_default=True,
)
@eClick.option(
    "--port",
    type=int,
    default=8000,
    help="Bind socket to this port. If 0, an available port will be picked.",
    show_default=True,
)
@eClick.option("--uds", type=str, default=None, help="Bind to a UNIX domain socket.")
@eClick.option(
    "--fd", type=int, default=None, help="Bind to socket from this file descriptor."
)
@eClick.option("--reload", is_flag=True, default=False, help="Enable auto-reload.")
@eClick.option(
    "--reload-dir",
    "reload_dirs",
    multiple=True,
    help="Set reload directories explicitly, instead of using the current working"
    " directory.",
    type=eClick.Path(exists=True),
)
@eClick.option(
    "--reload-include",
    "reload_includes",
    multiple=True,
    help="Set glob patterns to include while watching for files. Includes '*.py' "
    "by default; these defaults can be overridden with `--reload-exclude`. "
    "This option has no effect unless watchfiles is installed.",
)
@eClick.option(
    "--reload-exclude",
    "reload_excludes",
    multiple=True,
    help="Set glob patterns to exclude while watching for files. Includes "
    "'.*, .py[cod], .sw.*, ~*' by default; these defaults can be overridden "
    "with `--reload-include`. This option has no effect unless watchfiles is "
    "installed.",
)
@eClick.option(
    "--reload-delay",
    type=float,
    default=0.25,
    show_default=True,
    help="Delay between previous and next check if application needs to be."
    " Defaults to 0.25s.",
)
@eClick.option(
    "--workers",
    default=None,
    type=int,
    help="Number of worker processes. Defaults to the $WEB_CONCURRENCY environment"
    " variable if available, or 1. Not valid with --reload.",
)
@eClick.option(
    "--loop",
    type=LOOP_CHOICES,
    default="auto",
    help="Event loop implementation.",
    show_default=True,
)
@eClick.option(
    "--http",
    type=HTTP_CHOICES,
    default="auto",
    help="HTTP protocol implementation.",
    show_default=True,
)
@eClick.option(
    "--ws",
    type=WS_CHOICES,
    default="auto",
    help="WebSocket protocol implementation.",
    show_default=True,
)
@eClick.option(
    "--ws-max-size",
    type=int,
    default=16777216,
    help="WebSocket max size message in bytes",
    show_default=True,
)
@eClick.option(
    "--ws-max-queue",
    type=int,
    default=32,
    help="The maximum length of the WebSocket message queue.",
    show_default=True,
)
@eClick.option(
    "--ws-ping-interval",
    type=float,
    default=20.0,
    help="WebSocket ping interval in seconds.",
    show_default=True,
)
@eClick.option(
    "--ws-ping-timeout",
    type=float,
    default=20.0,
    help="WebSocket ping timeout in seconds.",
    show_default=True,
)
@eClick.option(
    "--ws-per-message-deflate",
    type=bool,
    default=True,
    help="WebSocket per-message-deflate compression",
    show_default=True,
)
@eClick.option(
    "--lifespan",
    type=LIFESPAN_CHOICES,
    default="auto",
    help="Lifespan implementation.",
    show_default=True,
)
@eClick.option(
    "--interface",
    type=INTERFACE_CHOICES,
    default="auto",
    help="Select ASGI3, ASGI2, or WSGI as the application interface.",
    show_default=True,
)
@eClick.option(
    "--env-file",
    type=eClick.Path(exists=True),
    default=None,
    help="Environment configuration file.",
    show_default=True,
)
@eClick.option(
    "--log-level",
    type=LEVEL_CHOICES,
    default=None,
    help="Log level. [default: info]",
    show_default=True,
)
@eClick.option(
    "--access-log/--no-access-log",
    is_flag=True,
    default=True,
    help="Enable/Disable access log.",
)
@eClick.option(
    "--use-colors/--no-use-colors",
    is_flag=True,
    default=None,
    help="Enable/Disable colorized logging.",
)
@eClick.option(
    "--proxy-headers/--no-proxy-headers",
    is_flag=True,
    default=True,
    help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to "
    "populate remote address info.",
)
@eClick.option(
    "--server-header/--no-server-header",
    is_flag=True,
    default=True,
    help="Enable/Disable default Server header.",
)
@eClick.option(
    "--date-header/--no-date-header",
    is_flag=True,
    default=True,
    help="Enable/Disable default Date header.",
)
@eClick.option(
    "--forwarded-allow-ips",
    type=str,
    default=None,
    help="Comma separated list of IPs to trust with proxy headers. Defaults to"
    " the $FORWARDED_ALLOW_IPS environment variable if available, or '127.0.0.1'.",
)
@eClick.option(
    "--root-path",
    type=str,
    default="",
    help="Set the ASGI 'root_path' for applications submounted below a given URL path.",
)
@eClick.option(
    "--limit-concurrency",
    type=int,
    default=None,
    help="Maximum number of concurrent connections or tasks to allow, before issuing"
    " HTTP 503 responses.",
)
@eClick.option(
    "--backlog",
    type=int,
    default=2048,
    help="Maximum number of connections to hold in backlog",
)
@eClick.option(
    "--limit-max-requests",
    type=int,
    default=None,
    help="Maximum number of requests to service before terminating the process.",
)
@eClick.option(
    "--timeout-keep-alive",
    type=int,
    default=5,
    help="Close Keep-Alive connections if no new data is received within this timeout.",
    show_default=True,
)
@eClick.option(
    "--timeout-graceful-shutdown",
    type=int,
    default=None,
    help="Maximum number of seconds to wait for graceful shutdown.",
)
@eClick.option(
    "--ssl-keyfile", type=str, default=None, help="SSL key file", show_default=True
)
@eClick.option(
    "--ssl-certfile",
    type=str,
    default=None,
    help="SSL certificate file",
    show_default=True,
)
@eClick.option(
    "--ssl-keyfile-password",
    type=str,
    default=None,
    help="SSL keyfile password",
    show_default=True,
)
@eClick.option(
    "--ssl-version",
    type=int,
    default=int(SSL_PROTOCOL_VERSION),
    help="SSL version to use (see stdlib ssl module's)",
    show_default=True,
)
@eClick.option(
    "--ssl-cert-reqs",
    type=int,
    default=int(ssl.CERT_NONE),
    help="Whether client certificate is required (see stdlib ssl module's)",
    show_default=True,
)
@eClick.option(
    "--ssl-ca-certs",
    type=str,
    default=None,
    help="CA certificates file",
    show_default=True,
)
@eClick.option(
    "--ssl-ciphers",
    type=str,
    default="TLSv1",
    help="Ciphers to use (see stdlib ssl module's)",
    show_default=True,
)
@eClick.option(
    "--header",
    "headers",
    multiple=True,
    help="Specify custom default HTTP response headers as a Name:Value pair",
)
# @eClick.option(
#     "--app-dir",
#     default="",
#     show_default=True,
#     help="Look for APP in the specified directory, by adding this to the PYTHONPATH."
#     " Defaults to the current working directory.",
# )
@eClick.option(
    "--h11-max-incomplete-event-size",
    "h11_max_incomplete_event_size",
    type=int,
    default=None,
    help="For h11, the maximum number of bytes to buffer of an incomplete event.",
)
@eClick.pass_context
def runserver(
    ctx: eClick.Context,
    host: str,
    port: int,
    uds: str,
    fd: int,
    loop: uvicorn_config.LoopSetupType,
    http: uvicorn_config.HTTPProtocolType,
    ws: uvicorn_config.WSProtocolType,
    ws_max_size: int,
    ws_max_queue: int,
    ws_ping_interval: float,
    ws_ping_timeout: float,
    ws_per_message_deflate: bool,
    lifespan: uvicorn_config.LifespanType,
    interface: uvicorn_config.InterfaceType,
    reload: bool,
    reload_dirs: list[str],
    reload_includes: list[str],
    reload_excludes: list[str],
    reload_delay: float,
    workers: int,
    env_file: str,
    log_level: str,
    access_log: bool,
    proxy_headers: bool,
    server_header: bool,
    date_header: bool,
    forwarded_allow_ips: str,
    root_path: str,
    limit_concurrency: int,
    backlog: int,
    limit_max_requests: int,
    timeout_keep_alive: int,
    timeout_graceful_shutdown: int | None,
    ssl_keyfile: str,
    ssl_certfile: str,
    ssl_keyfile_password: str,
    ssl_version: int,
    ssl_cert_reqs: int,
    ssl_ca_certs: str,
    ssl_ciphers: str,
    headers: list[str],
    use_colors: bool,
    # app_dir: str,
    h11_max_incomplete_event_size: int | None,
):
    """- Starts Uvicorn Server -"""
    ellar_project_meta = t.cast(t.Optional[EllarCLIService], ctx.meta.get(ELLAR_META))

    if not ellar_project_meta:
        raise EllarCLIException("No pyproject.toml file found.")

    if not ellar_project_meta.has_meta:
        raise EllarCLIException(
            "No available project found. please create ellar project with `ellar create-project 'project-name'`"
        )

    application_import_string = ellar_project_meta.project_meta.application
    current_config = ellar_project_meta.get_application_config()

    log_config = current_config.LOGGING_CONFIG
    _log_level = current_config.LOG_LEVEL

    _log_level = log_level if log_level else _log_level or LOG_LEVELS.info

    init_kwargs = {
        "host": host,
        "ws_max_queue": ws_max_queue,
        "port": port,
        "uds": uds,
        "fd": fd,
        "loop": loop,
        "http": http,
        "ws": ws,
        "ws_max_size": ws_max_size,
        "ws_per_message_deflate": ws_per_message_deflate,
        "ws_ping_interval": ws_ping_interval,
        "ws_ping_timeout": ws_ping_timeout,
        "timeout_graceful_shutdown": timeout_graceful_shutdown,
        "lifespan": lifespan,
        "env_file": env_file,
        "log_config": LOGGING_CONFIG if log_config is None else log_config,
        "log_level": _log_level.value if _log_level.value != "NOT_SET" else None,
        "access_log": access_log,
        "interface": interface,
        "reload": reload,
        "reload_dirs": reload_dirs or None,
        "reload_includes": reload_includes or None,
        "reload_excludes": reload_excludes or None,
        "reload_delay": reload_delay,
        "workers": workers,
        "proxy_headers": proxy_headers,
        "server_header": server_header,
        "date_header": date_header,
        "forwarded_allow_ips": forwarded_allow_ips,
        "root_path": root_path,
        "limit_concurrency": limit_concurrency,
        "backlog": backlog,
        "limit_max_requests": limit_max_requests,
        "timeout_keep_alive": timeout_keep_alive,
        "ssl_keyfile": ssl_keyfile,
        "ssl_certfile": ssl_certfile,
        "ssl_keyfile_password": ssl_keyfile_password,
        "h11_max_incomplete_event_size": h11_max_incomplete_event_size,
        "ssl_version": ssl_version,
        "ssl_cert_reqs": ssl_cert_reqs,
        "ssl_ca_certs": ssl_ca_certs,
        "ssl_ciphers": ssl_ciphers,
        "headers": [header.split(":", 1) for header in headers],
        "use_colors": use_colors,
        "factory": ellar_project_meta.is_app_callable(),
        # "app_dir": application_import_string.split(':')[0].replace('.', '/'),
    }

    now = datetime.now().strftime("%B %d, %Y - %X")
    print(
        f"\nStarting Uvicorn server...\n"
        f"{now}\n"
        f"Ellar version {ellar_version}, using settings {current_config.config_module!r}\n"
    )

    uvicorn_run(application_import_string, **init_kwargs)
