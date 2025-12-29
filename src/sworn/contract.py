from dataclasses import dataclass, field
from datetime import datetime
import time
from sworn.commitment import Commitment
from typing import Callable, Literal
from sworn.observability.observer import Observer
from sworn.types import ToolCall, ToolContext, VerificationResult, VerificationResultStatus
from sworn.execution import Execution, _context_execution
import inspect
from functools import wraps
from typing import Callable, Literal, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


@dataclass
class Contract:
    """A contract consisting of multiple commitments."""
    commitments: list[Commitment] = field(default_factory=list)
    on_violation: Callable[[VerificationResult], None] | None = None
    observer: Observer | None = None

    def execution(self) -> Execution:
        """Create a new execution context for this contract."""
        return Execution(_contract=self)

    @property
    def current_execution(self) -> Execution:
        """Get the current execution from context (for use by decorators)."""
        try:
            return _context_execution.get()
        except LookupError:
            raise RuntimeError(
                "Must be inside 'with contract.execution():' block")

    def _verify(self, execution: Execution, observer: Observer | None = None) -> list[VerificationResult]:
        """Verifies the execution against all commitments in the contract (internal)."""
        obs = observer if observer is not None else self.observer
        results: list[VerificationResult] = []

        for commitment in self.commitments:
            result: VerificationResult = commitment.verify(
                execution, observer=obs)
            results.append(result)

            if result.status == VerificationResultStatus.PASS:
                continue

            if commitment.on_violation:
                commitment.on_violation(result)
                continue

            if self.on_violation:
                self.on_violation(result)

        covered_indices: set[int] = set()
        for result in results:
            covered_indices.update(result.cover)

        all_indices = set(range(len(execution.tool_calls)))
        uncovered_indices = all_indices - covered_indices

        covered = [execution.tool_calls[i] for i in covered_indices]
        uncovered = [execution.tool_calls[i] for i in uncovered_indices]

        if obs:
            obs.submit_coverage(covered, uncovered)

        return results

    def traced(self, func: Callable[P, R], function: Literal["sensor", "actuator"]) -> Callable[P, R]:
        """Decorator to trace a function with the contract's commitments."""

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            named_args: dict = dict(bound.arguments)

            start_time = time.time()
            error: Exception | None = None
            result = None

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                error = e
                raise
            finally:
                end_time = time.time()
                self.current_execution.tool_calls.append(
                    ToolCall(
                        tool_name=func.__name__,
                        function=function,
                        args=named_args,
                        tool_context=ToolContext(
                            started_at=datetime.fromtimestamp(start_time),
                            ended_at=datetime.fromtimestamp(end_time),
                            duration_ms=(end_time - start_time) * 1000
                        ),
                        tool_response=result,
                        error=error
                    )
                )

            return result

        return wrapper

    def sensor(self, func: Callable[P, R]) -> Callable[P, R]:
        """Decorator to trace a sensor function."""
        return self.traced(func, function="sensor")

    def actuator(self, func: Callable[P, R]) -> Callable[P, R]:
        """Decorator to trace an actuator function."""
        return self.traced(func, function="actuator")

    def add_commitment(self, commitment: Commitment) -> None:
        """Adds a commitment to the contract."""
        self.commitments.append(commitment)

    def get_terms(self) -> str:
        """Returns the combined terms of all commitments in the contract."""
        return "\n".join([commitment.get_term() for commitment in self.commitments])
