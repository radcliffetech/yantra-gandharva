from engines import EngineType

from .llm import LLMPartimentoEngine


def get_partimento_engine(engine_type: EngineType, call_llm=None):
    if engine_type == EngineType.ALGORITHMIC:
        from .algorithmic import AlgorithmicPartimentoEngine

        return AlgorithmicPartimentoEngine()
    else:
        if call_llm is None:
            from lib.utils.llm_utils import call_llm as default_call_llm

            call_llm = default_call_llm
        return LLMPartimentoEngine(call_llm)
