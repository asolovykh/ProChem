import logging

logger = logging.getLogger(__name__)


def logs_call(logger_obj=logger, /, is_class_method=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if is_class_method:
                if len(args) > 1:
                    logger_obj.info(
                        f"Class method {func.__name__} called with parameters {args[1:] if args else []} and {kwargs if kwargs else {}}"
                    )
                else:
                    logger_obj.info(
                        f"Class method {func.__name__} called with parameters [] and {kwargs if kwargs else {}}"
                    )
            else:
                logger_obj.info(
                    f"Function {func.__name__} called with parameters {args if args else []} and {kwargs if kwargs else {}}"
                )
            result = func(*args, **kwargs)
            (
                logger_obj.info(f"Function {func.__name__} finished")
                if not is_class_method
                else logger_obj.info(f"Class method {func.__name__} finished")
            )
            return result

        return wrapper

    return decorator
