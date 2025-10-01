from sqlalchemy.exc import SQLAlchemyError

import logging

logger = logging.getLogger(__name__)


def commit_to_db(session, view, success_callback=None, error_callback=None):
    """
    Essaie de commit la session.
    """
    try:
        session.commit()
        if success_callback:
            success_callback()
        return True
    except SQLAlchemyError as e:
        session.rollback()
        # Logger dans sentry
        logger.error(e)
        if error_callback:
            error_callback(str(e))
        else:
            view.message_db_error(str(e))
        return False
