from .core import handler_map as core_handler_map
from .firebase import handler_map as firebase_handler_map
from .jazz import handler_map as jazz_handlers
from .partimento import handler_map as partimento_handlers

handler_map = {
    **partimento_handlers,
    **jazz_handlers,
    **firebase_handler_map,
    **core_handler_map,
}
