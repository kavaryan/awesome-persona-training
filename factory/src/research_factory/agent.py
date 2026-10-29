"""Supervised, bounded Codex CLI invocation with inspectable inputs and outputs."""

import json
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path

from jsonschema import validate


def wire_schema(schema):
    """Strict output APIs support a subset; enforce the full schema locally afterward."""
    if isinstance(schema, dict):
        return {key: wire_schema(value) for key, value in schema.items() if key != "uniqueItems"}
    if isinstance(schema, list):
        return [wire_schema(value) for value in schema]
    return schema


class CodeAgent:
    def __init__(
        self, executable="codex", model=None, timeout=600, total_seconds=2400, reasoning_effort="medium"
    ):
        self.executable = executable
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout
        self.deadline = time.monotonic() + total_seconds

    def call(self, prompt, schema, directory, name, *, search=False):
        directory = Path(directory).resolve()
        directory.mkdir(parents=True, exist_ok=True)
        schema_path = directory / f"{name}.schema.json"
        output = directory / f"{name}.answer.json"
        schema_path.write_text(json.dumps(wire_schema(schema)))
        (directory / f"{name}.prompt.txt").write_text(prompt)
        if not shutil.which(self.executable):
            raise RuntimeError(
                "Codex CLI not found; install and authenticate it, and use --agent if it is outside PATH"
            )
        remaining = min(self.timeout, self.deadline - time.monotonic())
        if remaining <= 0:
            raise TimeoutError("Bootstrap agent time budget exhausted; rerun with --resume")
        command = [
            self.executable,
            "exec",
            "--skip-git-repo-check",
            "--ephemeral",
            "--sandbox",
            "workspace-write",
            "-c",
            'approval_policy="never"',
            "-c",
            "sandbox_workspace_write.network_access=true",
            "-c",
            f'web_search="{"live" if search else "disabled"}"',
            "-c",
            f'model_reasoning_effort="{self.reasoning_effort}"',
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output),
            "--color",
            "never",
            "--json",
            "-C",
            str(directory),
        ]
        if self.model:
            command += ["--model", self.model]
        command.append("-")
        output.unlink(missing_ok=True)
        started = time.monotonic()
        print(f"Agent phase {name}: budget {int(remaining)}s", flush=True)
        with (
            (directory / f"{name}.events.jsonl").open("w") as events,
            (directory / f"{name}.stderr.log").open("w") as errors,
        ):
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=events,
                stderr=errors,
                text=True,
                cwd=directory,
                start_new_session=True,
            )
            try:
                proc.communicate(prompt, timeout=remaining)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                raise TimeoutError(f"Agent phase {name} timed out; checkpoint retained") from None
        if proc.returncode != 0 or not output.exists():
            raise RuntimeError(
                f"Agent phase {name} failed (exit {proc.returncode}); inspect .bootstrap logs locally"
            )
        answer = json.loads(output.read_text())
        validate(answer, schema)
        print(f"Agent phase {name}: completed in {int(time.monotonic() - started)}s", flush=True)
        return answer
