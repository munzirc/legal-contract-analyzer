
import json
import os
import logging
from uuid import UUID
from typing import Any, Callable
from google.genai.errors import APIError

from pydantic import ValidationError
from dotenv import load_dotenv
from google import genai
from google.genai.interactions import FunctionCallStep, Interaction
from app.exceptions.agent_exceptions import get_api_error_message
from app.services.agent_interaction_services.agent_tools.progress_messages import get_progress_message
from app.services.agent_interaction_services.agent_tools.system_instruction import (
    TOOL_EXECUTION_INSTRUCTION, FINALIZATION_INSTRUCTION,BUDGET_EXHAUSTED_INSTRUCTION
)
from app.services.agent_interaction_services.agent_tools.tool_declarations import (
    set_document_serach_declaration,
    get_document_structure_declaration,
    get_section_declaration,
    ToolDeclaration,
)
from app.services.agent_interaction_services.agent_tools.execute_tool_round import (
    execute_tool_round,
)
from app.schemas.agent_response_schema import (
    AgentResponse,
    AgentRunResult,
)
from app.schemas.tool_result_schema import (
    FunctionResult, FunctionResultContent
)
from app.schemas.input_schema import (
    SelectedDocument,
    Input,
)

load_dotenv()

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-3.1-flash-lite"
MAX_TOOL_CALLS_PER_ROUND = 5
MAX_ROUNDS = 5

TOOL_DECLARATIONS: list[ToolDeclaration] = [
    set_document_serach_declaration,
    get_document_structure_declaration,
    get_section_declaration,
]

RESPONSE_FORMAT = {
    "type": "text",
    "mime_type": "application/json",
    "schema": AgentResponse.model_json_schema(),
}

ProgressCallback = Callable[[str], None]

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])



def get_function_calls(
    interaction: Interaction,
) -> list[FunctionCallStep]:
    return [
        step
        for step in interaction.steps
        if step.type == "function_call"
    ]


def parse_final_response(
    interaction: Interaction,
) -> AgentRunResult:
    """Validate and return the agent's final JSON response."""

    output_text = interaction.output_text

    if not output_text:
        logger.error("Agent finished without producing output text.")
        return AgentRunResult(
            interaction_id=interaction.id,
            completed=False,
            error="The agent did not produce a final answer.",
        )

    try:
        response = AgentResponse.model_validate_json(output_text)

    except (ValidationError, ValueError):
        logger.exception("Failed to parse the agent's final response.")
        return AgentRunResult(
            interaction_id=interaction.id,
            completed=False,
            error="The agent returned an invalid final response.",
        )

    return AgentRunResult(
        response=response,
        interaction_id=interaction.id,
        completed=True,
    )


def finalize_agent(
    interaction: Interaction,
    function_calls: list[FunctionCallStep],
    question: str,
) -> AgentRunResult:

    logger.warning(
        "Tool budget exhausted. Pending calls: %s",
        len(function_calls),
    )

    skipped_results: list[FunctionResult] = []

    for function_call in function_calls:
        logger.warning(
            "Skipping pending tool call: name=%s, call_id=%s",
            function_call.name,
            function_call.id,
        )

        skipped_results.append(
            FunctionResult(
                name=function_call.name,
                call_id=function_call.id,
                result=[
                    FunctionResultContent(
                        type="text",
                        text=(
                            "NOT EXECUTED: The application tool-execution "
                            "budget has been exhausted. This result contains "
                            "no document evidence. Do not treat this call as "
                            "successful. Use only information retrieved in "
                            "earlier rounds and disclose any limitations."
                        ),
                    )
                ],
            )
        )

    try:
        resolved_interaction = client.interactions.create(
            model=MODEL_NAME,
            previous_interaction_id=interaction.id,
            input=[
                result.model_dump(mode="json")
                for result in skipped_results
            ],
            system_instruction=BUDGET_EXHAUSTED_INSTRUCTION,
            stream=False,
        )

    except APIError as error:
        logger.exception(
            "Failed to resolve pending function calls."
        )

        return AgentRunResult(
            interaction_id=interaction.id,
            completed=False,
            error=get_api_error_message(error),
        )

    # Now generate the final structured answer in a separate call.
    return generate_final_response(
        interaction=resolved_interaction,
        question=question,
    )

def generate_final_response(
    interaction: Interaction,
    question: str,
) -> AgentRunResult:
    """Generate the final structured answer after tool execution."""

    logger.info("Generating final structured response.")

    final_input = (
        "The contract research phase is complete.\n\n"
        f"Original user question:\n{question}\n\n"
        "Using the contract information and tool results available in "
        "the preceding interaction history, produce the final answer "
        "and its supporting evidence.\n"
        "Return only the required AgentResponse structure."
    )

    try:
        final_interaction = client.interactions.create(
            model=MODEL_NAME,
            previous_interaction_id=interaction.id,
            input=final_input,
            system_instruction=FINALIZATION_INSTRUCTION,
            stream=False,
            response_format=RESPONSE_FORMAT,
        )

    except APIError as error:
        logger.exception("Gemini final response generation failed.")

        return AgentRunResult(
            interaction_id=interaction.id,
            completed=False,
            error=get_api_error_message(error),
        )

    logger.info(
        "Final response interaction received. Interaction ID: %s",
        final_interaction.id,
    )

    return parse_final_response(final_interaction)

def start_agent(
    question: str,
    document_ids: list[UUID],
    selected_documents: list[SelectedDocument],
    previous_interaction_id: str | None = None,
    progress_callback: ProgressCallback | None = None,
) -> AgentRunResult:

    initial_input = Input(
        question=question,
        selected_documents=selected_documents,
    )

    logger.info("========== AGENT START ==========")
    logger.info("Model: %s", MODEL_NAME)
    logger.info("Question: %s", question)
    logger.info(
        "Selected document IDs: %s",
        [str(doc_id) for doc_id in document_ids],
    )
    logger.info("Maximum rounds: %s", MAX_ROUNDS)
    logger.info(
        "Maximum tool calls per round: %s",
        MAX_TOOL_CALLS_PER_ROUND,
    )

    # 1. Start the tool-execution phase.
    try:
        interaction = client.interactions.create(
            model=MODEL_NAME,
            input=json.dumps(initial_input.model_dump(mode="json")),
            system_instruction=TOOL_EXECUTION_INSTRUCTION,
            tools=TOOL_DECLARATIONS,
            stream=False,
            previous_interaction_id=previous_interaction_id,
            generation_config={"tool_choice": "any"},
        )

    except APIError as error:
        logger.exception("Gemini initial interaction failed.")

        return AgentRunResult(
            completed=False,
            error=get_api_error_message(error),
        )

    round_count = 0

    logger.info(
        "Initial interaction received. Interaction ID: %s",
        interaction.id,
    )

    # 2. Execute the tool-calling loop.
    while True:

        function_calls = get_function_calls(interaction)

        logger.info("---------- ROUND %s ----------", round_count + 1)
        logger.info("Interaction ID: %s", interaction.id)
        logger.info(
            "Agent requested %d tool calls: %s",
            len(function_calls),
            [call.name for call in function_calls],
        )
        logger.info("Interaction status: %s", interaction.status)

        # No more function calls: move to final response generation.
        if not function_calls:

            result = generate_final_response(
                interaction=interaction,
                question=question,
            )

            if result.completed:
                logger.info("Agent completed successfully.")
                logger.info("Total tool rounds used: %s", round_count)
                logger.info("========== AGENT END ==========")

            return result

        # Tool execution budget exhausted.
        if round_count >= MAX_ROUNDS:

            logger.warning(
                "Maximum round limit reached. "
                "Gemini still requested %s tool call(s).",
                len(function_calls),
            )

            return finalize_agent(
                interaction=interaction,
                function_calls=function_calls,
                question=question,
            )

        round_count += 1

        # 3. Report progress for requested tools.
        for function_call in function_calls:

            logger.info(
                "Tool requested: name=%s, call_id=%s, arguments=%s",
                function_call.name,
                function_call.id,
                function_call.arguments,
            )

            if progress_callback is not None:
                progress_callback(
                    get_progress_message(function_call)
                )

        # 4. Execute requested tools.
        function_results: list[FunctionResult] = execute_tool_round(
            function_calls=function_calls,
            document_ids=document_ids,
            max_tool_calls=MAX_TOOL_CALLS_PER_ROUND,
        )

        logger.info("Tool results returned: %s", len(function_results))

        for index, result in enumerate(function_results, start=1):

            result_size = len(
                json.dumps(
                    result.model_dump(mode="json"),
                    ensure_ascii=False,
                )
            )

            logger.info(
                "Tool result %s: name=%s, result_size=%s characters",
                index,
                result.name,
                result_size,
            )

        # 5. Submit tool results and allow Gemini to continue.
        logger.info("Submitting tool results to Gemini.")

        try:
            interaction = client.interactions.create(
                model=MODEL_NAME,
                previous_interaction_id=interaction.id,
                input=[
                    result.model_dump(mode="json")
                    for result in function_results
                ],
                tools=TOOL_DECLARATIONS,
                system_instruction=TOOL_EXECUTION_INSTRUCTION,
                stream=False,
                generation_config={"tool_choice": "any"},
            )

        except APIError as error:
            logger.exception("Gemini follow-up interaction failed.")

            return AgentRunResult(
                completed=False,
                error=get_api_error_message(error),
            )

        logger.info(
            "Next interaction received. Interaction ID: %s",
            interaction.id,
        )