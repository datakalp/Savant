"""Module entrypoint function."""
import os
from pathlib import Path

from savant.config import ModuleConfig
from savant.deepstream.encoding import check_encoder_is_available
from savant.deepstream.pipeline import NvDsPipeline
from savant.deepstream.runner import NvDsPipelineRunner
from savant.gstreamer import Gst
from savant.utils.logging import get_logger, init_logging, update_logging
from savant.utils.sink_factories import sink_factory


def main(config_file_path: str):
    """Entrypoint for NvDsPipeline based module.

    :param config_file_path: Module configuration file path.
    """

    status_filepath = os.environ.get('SAVANT_STATUS_FILEPATH')
    if status_filepath is not None:
        status_filepath = Path(status_filepath)
        if status_filepath.exists():
            status_filepath.unlink()
        status_filepath.parent.mkdir(parents=True, exist_ok=True)

    # load default.yml and set up logging
    config = ModuleConfig().config

    init_logging(config.parameters['log_level'])

    # load module config
    config = ModuleConfig().load(config_file_path)

    # reconfigure savant logger with updated loglevel
    update_logging(config.parameters['log_level'])
    logger = get_logger('main')

    # possible exceptions will cause app to crash and log error by default
    # no need to handle exceptions here
    sink = sink_factory(config.pipeline.sink)

    Gst.init(None)

    if not check_encoder_is_available(config.parameters):
        return

    pipeline = NvDsPipeline(
        config.name,
        config.pipeline,
        **config.parameters,
    )

    try:
        with NvDsPipelineRunner(pipeline, status_filepath):
            try:
                for msg in pipeline.stream():
                    sink(msg, **dict(module_name=config.name))
            except Exception as exc:  # pylint: disable=broad-except
                logger.error(exc, exc_info=True)
                # TODO: Sometimes pipeline hangs when exit(1) or not exit at all is called.
                #       E.g. when the module has "req+connect" socket at the sink and
                #       sink adapter is not available.
                os._exit(1)  # pylint: disable=protected-access
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(exc, exc_info=True)
