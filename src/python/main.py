import logging
import logging.config
import os
import sys

import click
import yaml
from vuit.adi.commons.config.pythena import Pythena


# This allows us to have extra args like Automic/docker_run adds (exec_time...)
@click.command(
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True}
)
@click.option(
    "--env", type=click.Choice(["prd", "uat", "dev"]), default="dev", help="Environment"
)
@click.option(
    "--team",
    type=click.Choice(["acad", "admsol", "ident"]),
    required=True,
    help="Team name (for athena). You must set the ATHENA_SECRET environment variable.",
)
def main(env: str, team: str) -> None:

    # Get the base logger
    base_logger = configure_logging()

    # Create a context-aware logger.
    # Just adds env and team to all logs so they can be filtered on in graylog.
    context = {"env": env, "team": team}
    logger = logging.LoggerAdapter(base_logger, context)

    logger.info(" **** Starting test ***")

    profiles = team + "," + env
    # get Config file from athena
    try:
        pythenaObj = Pythena("test", env, team, profiles)
        properties_from_athena = pythenaObj.get_properties()
        if properties_from_athena is None:
            logger.error(
                "Can't get athena properties. Check environment variable ATHENA_SECRET."
            )
            sys.exit(1)

        # Example of getting a property. Update as needed.
        prop_value = pythenaObj.get_property_value(
            "property.name", properties_from_athena
        )

        # Your application logic here...
        logger.info(f"Property value: {prop_value}")

        logger.info(" **** Finished test ***")
    except Exception as e:
        logger.exception(f"Unhandled exception occurred: {e}")
        sys.exit(1)

    finally:
        # Properly close all handlers to flush buffers
        for handler in logging.root.handlers:
            handler.flush()
            handler.close()
        # Additional specific closure for your logger
        for handler in logging.getLogger("test").handlers:
            handler.flush()
            handler.close()


# Look for log config in multiple locations with priority order
def get_log_config_path():
    """
    Bends over backwards to find a logging configuration file.

    - Environment variable LOG_CONFIG_PATH takes precedence.
    - Local file ./log-config.yaml is checked next.
      - This is useful for local testing and will not be included in the docker image.
    - The "normal" batch docker path is used next : /ext-vol/app-conf/logging/log-config.yaml.
    - Finally, if no external config is found, a default configuration is returned.
    """
    # 1. Environment variable takes precedence
    if os.environ.get("LOG_CONFIG_PATH"):
        return os.environ.get("LOG_CONFIG_PATH")

    # 2. Project location : ./log-config.yaml
    # Useful for local / non docker testing
    # this log config should not be in the docker image
    if os.path.exists("./log-config.yaml"):
        return "./log-config.yaml"

    # 3. Docker/container path: /ext-vol/app-conf/logging
    if os.path.exists("/ext-vol/app-conf/logging/log-config.yaml"):
        return "/ext-vol/app-conf/logging/log-config.yaml"

    # 4. No external config found, return a default configuration dictionary
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                "format": "%(asctime)s %(levelname)-8s [%(filename)s %(lineno)d] : %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "gelf": {
                "class": "pygelf.GelfTcpHandler",
                "host": "vulogs.app.vanderbilt.edu",
                "port": 4545,
                "level": "INFO",
                "include_extra_fields": True,
                "_appName": "test",
                "_appType": "batch",
                "_facility": "Hill",
            },
        },
        "loggers": {
            "test": {
                "level": "INFO",
                "handlers": ["console", "gelf"],
                "propagate": False,
            },
            "root": {"level": "ERROR", "handlers": ["console", "gelf"]},
        },
    }


def configure_logging():
    """Setup logging configuration with fallbacks"""
    logger_name = "test"
    config = get_log_config_path()

    try:
        if isinstance(config, str) and os.path.exists(config):
            # It's a file path
            with open(config) as f:
                config_dict = yaml.safe_load(f.read())
            logging.config.dictConfig(config_dict)
            logging.getLogger(logger_name).debug(f"Logging configured from {config}")
        elif isinstance(config, dict):
            # It's a default config dictionary
            logging.config.dictConfig(config)
            logging.getLogger(logger_name).debug(
                "Logging configured with default settings"
            )
        else:
            raise ValueError("Invalid configuration returned")
    except Exception as e:
        # Ultimate fallback if something goes wrong with the config
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)-8s [%(filename)s %(lineno)d] : %(message)s",
            stream=sys.stdout,
        )
        logging.error(f"Error configuring logging: {e}")

    # Return the logger for this application
    return logging.getLogger(logger_name)


if __name__ == "__main__":
    main()
