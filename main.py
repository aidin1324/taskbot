from builder import multi_agentic_graph

from utils.utils import _print_event

thread_id = 1

config = {
    "configurable": {
        # The passenger_id is used in our flight tools to
        # fetch the user's flight information
        # Checkpoints are accessed by thread_id
        "thread_id": thread_id,
    }
}


async def main_interaction():
    _printed = set()
    print("Введите 'exit' для завершения чата.")
    while True:
        user_input = input("Ваше сообщение: ")
        if user_input.strip().lower() == "exit":
            break
        async for event in multi_agentic_graph.astream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_input,
                    },
                ],
            },
            config,
            stream_mode="values",
        ):
            _print_event(event, _printed)

if __name__ == "__main__":
    import asyncio
    # Для первоначального вызова можно использовать либо main, либо main_interaction
    asyncio.run(main_interaction())
