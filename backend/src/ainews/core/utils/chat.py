from ainews.core.schemas.chat_schemas import ChatMessage, LLMMessage


def to_llm_messages(
    messages: list[ChatMessage],
) -> list[LLMMessage]:
    result: list[LLMMessage] = []

    for message in messages:
        text = message.text

        if not text:
            continue

        result.append(
            LLMMessage(
                role=message.role,
                content=text,
            )
        )

    return result
