from engines import EngineType

from .llm import LLMJazzEngine


def get_jazz_engine(engine_type: EngineType, call_llm=None):
    if engine_type == EngineType.ALGORITHMIC:
        from .algorithmic import AlgorithmicJazzEngine

        return AlgorithmicJazzEngine()
    else:
        if call_llm is None:
            from lib.utils.llm_utils import call_llm as default_call_llm

            call_llm = default_call_llm
        return LLMJazzEngine(call_llm)
