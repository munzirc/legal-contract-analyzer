import logging


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(processName)s[%(process)d] | %(name)s | %(message)s",
    )

    # Show detailed logs only for the processing worker.
    logging.getLogger(
        "app.services.document_service.processing_worker"
    ).setLevel(logging.DEBUG)