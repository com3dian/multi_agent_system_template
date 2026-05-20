# Multi-Agent System Template Architecture

This template provides a minimal but runnable architecture for building LLM-based multi-agent systems
around a shared execution context. This template aims to provide a base structure that is widely
adopted in modern agentic framework, with neccessary components (llm, planning, tools, memory) but no
more customized setting. 

## Overview

The system is organized into four layers:

1. Context Layer (`src/context/`)
- Unified `ExecutionContext` abstraction for resources (CSV/TSV and SQLite in this template).
- `ContextFactory` auto-detects input source type and creates the right context implementation.

2. Orchestration Layer (`src/orchestrator/`)
- `Orchestrator` generates a plan from an objective.
- `PlanExecutor` executes plan steps sequentially.
- `StepExecutor` runs each step with parallel players, optional debate rounds, then synthesis.

3. Player Layer (`src/players/`)
- Role-configured players with prompts, tools, and model settings.
- Players can execute tasks, critique, revise, and synthesize.

4. Tool Layer (`src/tools/`)
- Context registry for step execution (`register_context`, `get_context`, `clear_registry`).
- Context-aware tools (overview, schema, field stats, samples, relationships, etc.).

## Execution Flow

1. User passes `source`, topology, and objective via CLI (`src/main.py`).
2. `create_context(...)` builds an `ExecutionContext`.
3. Objective is resolved from `--objective` or `--objective-file`.
4. `Orchestrator.generate_plan(...)` creates a `Plan` (Pydantic schema).
5. `PlanExecutor.execute(...)` runs each step:
- spawn N players from topology
- parallel task execution
- critique/revise debate loop
- synthesize to consolidated artifact
6. Final `ExecutionResult` contains step results, workspace artifacts, and final output.

## Core Contracts

1. Plan step schema (`src/core/schemas.py`)
- `task`, `player`, `rationale`
- `inputs` and `outputs` for workspace dataflow
- optional `target_resources`

2. Context contract (`src/context/base_context.py`)
- `resources`, `get_resource_info`, `read_resource`, `iter_resource`, `get_relationships`

3. Result contract (`src/core/schemas.py`)
- `ExecutionResult.final_workspace`
- `ExecutionResult.final_output`

## Current Supported Sources

1. Single CSV/TSV file
2. Directory of CSV/TSV files
3. List or dict of CSV/TSV files
4. SQLite database

## Extension Points

1. Add new contexts:
- Implement `ExecutionContext` subclass and register in `ContextFactory`.

2. Add new tools:
- Add tool functions in `src/tools/context_tools.py`.
- Bind them in `src/players/configs.py`.

3. Add new player roles:
- Add role prompt/tool bundle in `PLAYER_CONFIGS`.

4. Add custom topologies:
- Add entries in `src/topology.py`.
