import logging

from contextvars import ContextVar

from typing import Optional

from functools import wraps


# =========================================================
# Logger (Phase 8.6 Structured Logging)
# =========================================================
import json

try:
    from pythonjsonlogger import jsonlogger
    HAS_JSON_LOGGER = True
except ImportError:
    HAS_JSON_LOGGER = False

logger = logging.getLogger(__name__)
if HAS_JSON_LOGGER:
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.propagate = False


# =========================================================
# Trace Context
# =========================================================

_execution_id: ContextVar[Optional[int]] = ContextVar(
    "execution_id",
    default=None
)

_agent_name: ContextVar[Optional[str]] = ContextVar(
    "agent_name",
    default=None
)

_operation_name: ContextVar[Optional[str]] = ContextVar(
    "operation_name",
    default=None
)


# =========================================================
# Execution ID
# =========================================================

def set_execution_id(
    execution_id: Optional[int]
):
    _execution_id.set(
        execution_id
    )



from functools import wraps


# =========================================================
# Agent Trace Decorator
# =========================================================

def trace_agent(agent_name: str):

    def decorator(func):

        @wraps(func)
        def wrapper(state):

            set_agent_name(agent_name)

            trace_log(
                event="agent_started",
                message=f"Agent {agent_name} started"
            )

            try:

                result = func(state)

                trace_log(
                    event="agent_completed",
                    message=f"Agent {agent_name} completed"
                )

                return result

            except Exception as exc:

                trace_log(
                    event="agent_failed",
                    message=str(exc),
                    level=logging.ERROR
                )

                raise

        return wrapper

    return decorator


def get_execution_id() -> Optional[int]:

    return _execution_id.get()


# =========================================================
# Agent Name
# =========================================================

def set_agent_name(
    agent_name: Optional[str]
):
    _agent_name.set(
        agent_name
    )


def get_agent_name() -> Optional[str]:

    return _agent_name.get()


# =========================================================
# Operation Name
# =========================================================

def set_operation_name(
    operation_name: Optional[str]
):
    _operation_name.set(
        operation_name
    )


def get_operation_name() -> Optional[str]:

    return _operation_name.get()


# =========================================================
# Clear Trace Context
# =========================================================

def clear_trace_context():

    _execution_id.set(
        None
    )

    _agent_name.set(
        None
    )

    _operation_name.set(
        None
    )


# =========================================================
# Trace Logger
# =========================================================

def trace_log(
    event: str,
    message: str = "",
    level: int = logging.INFO
):

    execution_id = (
        get_execution_id()
    )

    agent_name = (
        get_agent_name()
    )

    operation_name = (
        get_operation_name()
    )

    parts = [
        f"TRACE | event={event}"
    ]

    # -----------------------------------------------------
    # Execution
    # -----------------------------------------------------

    if execution_id is not None:

        parts.append(
            f"execution_id={execution_id}"
        )

    # -----------------------------------------------------
    # Agent
    # -----------------------------------------------------

    if agent_name:

        parts.append(
            f"agent={agent_name}"
        )

    # -----------------------------------------------------
    # Operation
    # -----------------------------------------------------

    if operation_name:

        parts.append(
            f"operation={operation_name}"
        )

    # -----------------------------------------------------
    # Additional message
    # -----------------------------------------------------

    if message:

        parts.append(
            message
        )

    logger.log(
        level,
        " | ".join(parts)
    )