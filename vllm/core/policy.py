from collections import deque
from typing import Deque

from vllm.sequence import SequenceGroup


class Policy:

    def get_priority(
        self,
        now: float,
        seq_group: SequenceGroup,
    ) -> float:
        raise NotImplementedError

    def sort_by_priority(
        self,
        now: float,
        seq_groups: Deque[SequenceGroup],
    ) -> Deque[SequenceGroup]:
        return deque(
            sorted(
                seq_groups,
                key=lambda seq_group: self.get_priority(now, seq_group),
                reverse=True,
            ))


class FCFS(Policy):

    def get_priority(
        self,
        now: float,
        seq_group: SequenceGroup,
    ) -> float:
        return now - seq_group.arrival_time
    
class STATIC(Policy):

    def get_priority(
        self,
        now: float,
        seq_group: SequenceGroup,
    ) -> float:
        if seq_group.sampling_params.priority is None:
            return float('-inf')
        return seq_group.sampling_params.priority
    
class SJF(Policy):

    def get_priority(
        self,
        now: float,
        seq_group: SequenceGroup,
    ) -> float:
        return -seq_group.sampling_params.max_tokens
    
# Large Data First
class LDF(Policy):
    
        def get_priority(
            self,
            now: float,
            seq_group: SequenceGroup,
        ) -> float:
            data_size = 0
            for _, seq in seq_group.seqs_dict.items():
                data_size += len(seq.data.prompt_token_ids) + len(seq.data.output_token_ids)
            return data_size
        
class LCFS(Policy):

    def get_priority(
        self,
        now: float,
        seq_group: SequenceGroup,
    ) -> float:
        return seq_group.arrival_time - now


class PolicyFactory:

    _POLICY_REGISTRY = {
        'fcfs': FCFS,
        'static': STATIC,
        'sjf': SJF,
        'ldf': LDF,
        'lcfs': LCFS,
    }

    @classmethod
    def get_policy(cls, policy_name: str, **kwargs) -> Policy:
        return cls._POLICY_REGISTRY[policy_name](**kwargs)
