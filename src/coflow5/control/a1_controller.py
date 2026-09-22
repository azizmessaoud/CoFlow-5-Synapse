from __future__ import annotations

from typing import Mapping, Protocol

from coflow5.control.safety import ActionProposal, ProposalSource


class SafeSignalSubmission(Protocol):
    def submit(
        self,
        proposal: ActionProposal,
        *,
        simulation_time: float,
        pedestrian_remaining_clearance: Mapping[str, float] | None = None,
    ): ...


class A1FlowController:
    """Owns one safe submission capability; it never receives a raw TraCI connection."""

    def __init__(self, executor: SafeSignalSubmission) -> None:
        self.__executor = executor

    def propose(
        self,
        *,
        proposal_id: str,
        signal_id: str,
        phase_id: str,
        simulation_time: float,
        pedestrian_remaining_clearance: Mapping[str, float] | None = None,
    ):
        return self.__submit(
            proposal_id=proposal_id,
            signal_id=signal_id,
            phase_id=phase_id,
            source=ProposalSource.A1_FLOW,
            simulation_time=simulation_time,
            pedestrian_remaining_clearance=pedestrian_remaining_clearance,
        )

    def human_override(
        self,
        *,
        proposal_id: str,
        signal_id: str,
        phase_id: str,
        simulation_time: float,
        pedestrian_remaining_clearance: Mapping[str, float] | None = None,
    ):
        return self.__submit(
            proposal_id=proposal_id,
            signal_id=signal_id,
            phase_id=phase_id,
            source=ProposalSource.HUMAN_OVERRIDE,
            simulation_time=simulation_time,
            pedestrian_remaining_clearance=pedestrian_remaining_clearance,
        )

    def __submit(
        self,
        *,
        proposal_id: str,
        signal_id: str,
        phase_id: str,
        source: ProposalSource,
        simulation_time: float,
        pedestrian_remaining_clearance: Mapping[str, float] | None,
    ):
        proposal = ActionProposal(proposal_id, signal_id, phase_id, source)
        return self.__executor.submit(
            proposal,
            simulation_time=simulation_time,
            pedestrian_remaining_clearance=pedestrian_remaining_clearance,
        )
