import asyncio
import time
from typing import Any

from fastapi_agent_observability import Observability, get_langchain_callback


class AgentWorkflows:
    """Simulated AI agents demonstrating hierarchical tracing with fastapi-agent-observability."""

    def __init__(self, obs: Observability) -> None:
        self.obs = obs

    def run_research(self, topic: str, depth: str = "standard") -> dict[str, Any]:
        """
        Executes a multi-step research agent workflow:
        Root Chain -> Web Search Tool -> Ranking Chain -> LLM Synthesis
        """
        with self.obs.tracer.start_run(
            name="research_agent_workflow",
            run_type="chain",
            inputs={"topic": topic, "depth": depth},
        ) as root_run:
            # Step 1: Web search tool
            with self.obs.tracer.start_run(
                name="search_knowledge_base",
                run_type="tool",
                inputs={"query": topic, "max_results": 5 if depth == "deep" else 3},
            ) as tool_run:
                time.sleep(0.05)  # Simulate search latency
                mock_docs = [
                    {"id": 1, "title": f"Intro to {topic}", "snippet": f"Fundamental concepts of {topic}."},
                    {"id": 2, "title": f"Best Practices for {topic}", "snippet": f"Modern patterns in {topic}."},
                    {"id": 3, "title": f"Observability & Tracing in {topic}", "snippet": f"Capturing spans for {topic}."},
                ]
                tool_run.set_outputs({"retrieved_docs": mock_docs, "total": len(mock_docs)})

            # Step 2: Content ranking
            with self.obs.tracer.start_run(
                name="rank_and_filter",
                run_type="chain",
                inputs={"documents_count": len(mock_docs)},
            ) as filter_run:
                time.sleep(0.02)
                ranked_docs = mock_docs[:2]
                filter_run.set_outputs({"top_results": ranked_docs})

            # Step 3: LLM generation
            with self.obs.tracer.start_run(
                name="llm_synthesize_report",
                run_type="llm",
                inputs={
                    "model": "gpt-4o-mini-simulator",
                    "temperature": 0.3,
                    "prompt": f"Synthesize a clear summary for topic: '{topic}' based on retrieved sources.",
                },
            ) as llm_run:
                time.sleep(0.08)  # Simulate model latency
                summary = (
                    f"Research Summary for '{topic}':\n"
                    f"- Overview: Key aspects regarding {topic} have been retrieved.\n"
                    f"- Status: Analyzed {len(ranked_docs)} primary references with high confidence.\n"
                    f"- Recommendation: Fast local-first telemetry allows instant tracing of this query."
                )
                llm_run.set_outputs({
                    "completion": summary,
                    "tokens_used": {"prompt": 142, "completion": 76, "total": 218},
                })

            result = {
                "topic": topic,
                "summary": summary,
                "sources_used": len(ranked_docs),
                "trace_id": root_run.trace_id,
                "root_run_id": root_run.id,
            }
            root_run.set_outputs(result)
            return result

    def run_calculation(self, expression: str, target_unit: str = "metric") -> dict[str, Any]:
        """
        Executes a math & unit conversion agent:
        Root Chain -> Evaluation Tool -> Unit Conversion Tool
        """
        with self.obs.tracer.start_run(
            name="math_calculation_workflow",
            run_type="chain",
            inputs={"expression": expression, "target_unit": target_unit},
        ) as root_run:
            # Step 1: Evaluate expression safely
            with self.obs.tracer.start_run(
                name="safe_eval_expression",
                run_type="tool",
                inputs={"expression": expression},
            ) as eval_run:
                time.sleep(0.01)
                allowed_chars = set("0123456789+-*/(). ")
                if not set(expression).issubset(allowed_chars):
                    error_msg = f"Invalid expression characters in '{expression}'"
                    eval_run.set_error(error_msg)
                    raise ValueError(error_msg)

                # Evaluates basic arithmetic
                raw_result = float(eval(expression, {"__builtins__": None}, {}))
                eval_run.set_outputs({"raw_result": raw_result})

            # Step 2: Convert or format
            with self.obs.tracer.start_run(
                name="unit_formatter",
                run_type="tool",
                inputs={"value": raw_result, "target_unit": target_unit},
            ) as unit_run:
                time.sleep(0.01)
                if target_unit == "scientific":
                    formatted = f"{raw_result:e}"
                elif target_unit == "percentage":
                    formatted = f"{raw_result * 100:.2f}%"
                else:
                    formatted = f"{raw_result:,.4f}".rstrip("0").rstrip(".")

                unit_run.set_outputs({"formatted_result": formatted})

            outputs = {
                "expression": expression,
                "value": raw_result,
                "formatted": formatted,
                "trace_id": root_run.trace_id,
                "root_run_id": root_run.id,
            }
            root_run.set_outputs(outputs)
            return outputs

    def run_failing_task(self, fail_step: str = "external_api") -> dict[str, Any]:
        """
        Demonstrates how errors during execution are automatically captured in traces.
        """
        with self.obs.tracer.start_run(
            name="faulty_agent_pipeline",
            run_type="chain",
            inputs={"fail_step": fail_step},
        ):
            with self.obs.tracer.start_run(
                name="step_1_validation",
                run_type="tool",
                inputs={"status": "checking_preconditions"},
            ) as step1:
                time.sleep(0.01)
                step1.set_outputs({"valid": True})

            if fail_step == "external_api":
                with self.obs.tracer.start_run(
                    name="step_2_external_upstream_call",
                    run_type="tool",
                    inputs={"endpoint": "https://api.upstream-service.internal/v1/predict"},
                ):
                    time.sleep(0.02)
                    raise ConnectionResetError("Connection reset by peer: 504 Gateway Timeout")

            elif fail_step == "llm_quota":
                with self.obs.tracer.start_run(
                    name="step_2_llm_inference",
                    run_type="llm",
                    inputs={"model": "gpt-4"},
                ):
                    time.sleep(0.02)
                    raise RuntimeError("RateLimitError: Rate limit exceeded (429 Too Many Requests)")

            else:
                raise ValueError(f"Unknown fail_step '{fail_step}' triggered")

    async def run_langchain_demo(self, query: str) -> dict[str, Any]:
        """
        Executes a LangChain run using get_langchain_callback(obs) if langchain-core is installed.
        """
        try:
            callback = get_langchain_callback(self.obs)
        except ImportError:
            return {
                "status": "skipped",
                "message": (
                    "langchain-core is not installed. To test LangChain callback tracing, "
                    "install it with: pip install 'fastapi-agent-observability[langchain]'"
                ),
                "installed": False,
            }

        # If installed, run simulated callback events:
        import uuid
        run_id = uuid.uuid4()
        callback.on_chain_start(
            serialized={"name": "LangChainAgentPipeline"},
            inputs={"input": query},
            run_id=run_id,
        )
        await asyncio.sleep(0.05)
        callback.on_tool_start(
            serialized={"name": "SearchTool"},
            input_str=query,
            run_id=uuid.uuid4(),
            parent_run_id=run_id,
        )
        await asyncio.sleep(0.02)
        callback.on_chain_end(
            outputs={"output": f"Simulated LangChain response for: {query}"},
            run_id=run_id,
        )
        return {
            "status": "success",
            "installed": True,
            "trace_id": str(run_id),
            "output": f"Simulated LangChain execution completed for: {query}",
        }
