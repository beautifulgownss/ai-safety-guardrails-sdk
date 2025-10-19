"""Core guard orchestration logic for the AI Safety Guardrails SDK."""

from __future__ import annotations

import inspect
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Set,
    Tuple,
)

Stage = Literal["pre", "post"]


class GuardError(Exception):
    """Base class for guard-related errors."""


class GuardConfigurationError(GuardError):
    """Raised when the guard is misconfigured."""


class GuardViolation(GuardError):
    """Raised when one or more rules fail."""

    def __init__(
        self,
        message: str,
        *,
        results: Sequence["RuleResult"],
        context: "RuleContext",
    ) -> None:
        super().__init__(message)
        self.results = list(results)
        self.context = context


class RBACError(GuardError):
    """Raised when RBAC requirements are not met for a rule."""


@dataclass
class RuleContext:
    """Context shared across rule evaluations."""

    inputs: Any
    output: Any = None
    metadata: MutableMapping[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def with_output(self, output: Any) -> "RuleContext":
        """Return a copy of the context with updated output."""
        new_context = RuleContext(
            inputs=self.inputs,
            output=output,
            metadata=dict(self.metadata),
            user_id=self.user_id,
            session_id=self.session_id,
            tags=list(self.tags),
        )
        return new_context


@dataclass
class RuleResult:
    """Structured outcome for a rule evaluation."""

    rule: str
    passed: bool
    stage: Stage
    severity: str
    latency_ms: float = 0.0
    details: Mapping[str, Any] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return self.passed


@dataclass
class GuardReport:
    """Aggregate summary of guard execution."""

    context: RuleContext
    pre_results: List[RuleResult]
    post_results: List[RuleResult]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.pre_results + self.post_results)

    @property
    def failures(self) -> List[RuleResult]:
        return [r for r in self.pre_results + self.post_results if not r.passed]


class BaseAuditLogger(ABC):
    """Interface for audit loggers."""

    @abstractmethod
    def log_event(self, event: Mapping[str, Any]) -> None:
        """Persist an audit event."""


class NullAuditLogger(BaseAuditLogger):
    """Audit logger that discards all events."""

    def log_event(self, event: Mapping[str, Any]) -> None:  # pragma: no cover - trivial
        return


class StdoutAuditLogger(BaseAuditLogger):
    """Audit logger that writes structured events to the standard logger."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or logging.getLogger("guardrails.audit")

    def log_event(self, event: Mapping[str, Any]) -> None:
        self._logger.info("guardrail_audit_event", extra={"event": dict(event)})


class PerformanceMonitor:
    """Simple performance monitor for tracking rule latency."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or logging.getLogger("guardrails.performance")

    def record(self, result: RuleResult, context: RuleContext) -> None:
        self._logger.debug(
            "guardrail_rule_latency",
            extra={
                "rule": result.rule,
                "latency_ms": result.latency_ms,
                "stage": result.stage,
                "session_id": context.session_id,
                "user_id": context.user_id,
            },
        )


class BaseRule(ABC):
    """Abstract base class for all guardrail rules."""

    severity: str = "high"

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        stages: Sequence[Stage] = ("post",),
        required_roles: Optional[Iterable[str]] = None,
        config: Optional[Mapping[str, Any]] = None,
        enabled: bool = True,
    ) -> None:
        if not stages:
            raise GuardConfigurationError("At least one stage must be specified for a rule.")
        self.name = name or self.__class__.__name__
        self.stages: Tuple[Stage, ...] = tuple(stages)
        self.required_roles: Set[str] = set(required_roles or [])
        self.config = dict(config or {})
        self.enabled = enabled

    def supports_stage(self, stage: Stage) -> bool:
        return stage in self.stages

    def validate_roles(self, assigned_roles: Iterable[str]) -> None:
        if not self.required_roles:
            return
        if not set(assigned_roles).issuperset(self.required_roles):
            raise RBACError(
                f"Rule '{self.name}' requires roles {sorted(self.required_roles)} "
                f"but only {sorted(set(assigned_roles))} were provided."
            )

    @abstractmethod
    def evaluate(self, payload: Any, context: RuleContext, stage: Stage) -> RuleResult:
        """Execute the rule and return a structured result."""

    async def evaluate_async(self, payload: Any, context: RuleContext, stage: Stage) -> RuleResult:
        """Async-friendly wrapper, override for non-blocking implementations."""
        return self.evaluate(payload, context, stage)


class Guard:
    """Primary interface for executing guardrail rules around model calls."""

    def __init__(
        self,
        rules: Sequence[BaseRule],
        *,
        audit_logger: Optional[BaseAuditLogger] = None,
        logger: Optional[logging.Logger] = None,
        performance_monitor: Optional[PerformanceMonitor] = None,
        rbac_resolver: Optional[Callable[[RuleContext], Iterable[str]]] = None,
        name: str = "guard",
    ) -> None:
        if not rules:
            raise GuardConfigurationError("At least one rule must be supplied to the guard.")
        self.rules = list(rules)
        self.logger = logger or logging.getLogger("guardrails.guard")
        self.audit_logger = audit_logger or NullAuditLogger()
        self.performance_monitor = performance_monitor or PerformanceMonitor(self.logger)
        self.rbac_resolver = rbac_resolver
        self.name = name

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def protect(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator that applies guard validation around sync and async callables."""
        if inspect.iscoroutinefunction(func):

            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                context = self._build_context(args, kwargs)
                await self._run_stage(
                    "pre",
                    context.inputs,
                    context,
                    raise_on_failure=True,
                )
                result = await func(*args, **kwargs)
                context_with_output = context.with_output(result)
                await self._run_stage(
                    "post",
                    context_with_output.output,
                    context_with_output,
                    raise_on_failure=True,
                )
                return result

            return async_wrapper

        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            context = self._build_context(args, kwargs)
            self._run_stage_sync(
                "pre",
                context.inputs,
                context,
                raise_on_failure=True,
            )
            result = func(*args, **kwargs)
            context_with_output = context.with_output(result)
            self._run_stage_sync(
                "post",
                context_with_output.output,
                context_with_output,
                raise_on_failure=True,
            )
            return result

        return sync_wrapper

    def check(
        self,
        payload: Any,
        *,
        stage: Stage = "post",
        context: Optional[RuleContext] = None,
    ) -> GuardReport:
        """Run guardrails manually on arbitrary payloads."""
        context = context or RuleContext(inputs=None, output=None, metadata={})
        if stage == "pre":
            context.inputs = payload
            pre_results = self._run_stage_sync(
                "pre",
                payload,
                context,
                raise_on_failure=False,
            )
            post_results: List[RuleResult] = []
        else:
            pre_results = []
            context = context.with_output(payload)
            post_results = self._run_stage_sync(
                "post",
                payload,
                context,
                raise_on_failure=False,
            )
        return GuardReport(context=context, pre_results=pre_results, post_results=post_results)

    async def check_async(
        self,
        payload: Any,
        *,
        stage: Stage = "post",
        context: Optional[RuleContext] = None,
    ) -> GuardReport:
        """Async variant of ``check``."""
        context = context or RuleContext(inputs=None, output=None, metadata={})
        if stage == "pre":
            context.inputs = payload
            pre_results = await self._run_stage(
                "pre",
                payload,
                context,
                raise_on_failure=False,
            )
            post_results: List[RuleResult] = []
        else:
            pre_results = []
            context = context.with_output(payload)
            post_results = await self._run_stage(
                "post",
                payload,
                context,
                raise_on_failure=False,
            )
        return GuardReport(context=context, pre_results=pre_results, post_results=post_results)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _build_context(self, args: Sequence[Any], kwargs: Mapping[str, Any]) -> RuleContext:
        metadata: Dict[str, Any] = {"guard_name": self.name}
        return RuleContext(inputs={"args": args, "kwargs": kwargs}, metadata=metadata)

    def _rules_for_stage(self, stage: Stage) -> List[BaseRule]:
        return [rule for rule in self.rules if rule.enabled and rule.supports_stage(stage)]

    def _resolve_roles(self, context: RuleContext) -> Iterable[str]:
        if self.rbac_resolver is None:
            return ()
        return self.rbac_resolver(context)

    def _run_stage_sync(
        self,
        stage: Stage,
        payload: Any,
        context: RuleContext,
        *,
        raise_on_failure: bool,
    ) -> List[RuleResult]:
        results = []
        roles = list(self._resolve_roles(context))
        for rule in self._rules_for_stage(stage):
            try:
                rule.validate_roles(roles)
                result = self._execute_rule(rule, payload, context, stage)
                results.append(result)
                self._after_rule(result, context)
                if not result.passed and raise_on_failure:
                    raise GuardViolation(
                        f"Guardrail '{rule.name}' failed during {stage}-stage validation.",
                        results=[result],
                        context=context,
                    )
            except Exception as exc:  # pragma: no cover - defensive branch
                self.logger.exception("Rule '%s' raised an unexpected error", rule.name)
                raise GuardError(str(exc)) from exc
        return results

    async def _run_stage(
        self,
        stage: Stage,
        payload: Any,
        context: RuleContext,
        *,
        raise_on_failure: bool,
    ) -> List[RuleResult]:
        results: List[RuleResult] = []
        roles = list(self._resolve_roles(context))
        for rule in self._rules_for_stage(stage):
            try:
                rule.validate_roles(roles)
                result = await self._execute_rule_async(rule, payload, context, stage)
                results.append(result)
                self._after_rule(result, context)
                if not result.passed and raise_on_failure:
                    raise GuardViolation(
                        f"Guardrail '{rule.name}' failed during {stage}-stage validation.",
                        results=[result],
                        context=context,
                    )
            except Exception as exc:  # pragma: no cover - defensive branch
                self.logger.exception("Rule '%s' raised an unexpected error", rule.name)
                raise GuardError(str(exc)) from exc
        return results

    def _execute_rule(
        self,
        rule: BaseRule,
        payload: Any,
        context: RuleContext,
        stage: Stage,
    ) -> RuleResult:
        start = time.perf_counter()
        result = rule.evaluate(payload, context, stage)
        latency_ms = (time.perf_counter() - start) * 1000
        result.latency_ms = latency_ms
        return result

    async def _execute_rule_async(
        self,
        rule: BaseRule,
        payload: Any,
        context: RuleContext,
        stage: Stage,
    ) -> RuleResult:
        start = time.perf_counter()
        result = await rule.evaluate_async(payload, context, stage)
        latency_ms = (time.perf_counter() - start) * 1000
        result.latency_ms = latency_ms
        return result

    def _after_rule(self, result: RuleResult, context: RuleContext) -> None:
        event = {
            "rule": result.rule,
            "passed": result.passed,
            "stage": result.stage,
            "latency_ms": result.latency_ms,
            "severity": result.severity,
            "details": dict(result.details),
            "user_id": context.user_id,
            "session_id": context.session_id,
            "tags": list(context.tags),
        }
        self.audit_logger.log_event(event)
        self.performance_monitor.record(result, context)
        if not result.passed:
            self.logger.warning("Guardrail failed: %s", event)
        else:
            self.logger.debug("Guardrail passed: %s", event)
