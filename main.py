from agent import StudyAssistantAgent


def main():
    print("=" * 60)
    print(" AI Learning & Study Assistant (RAG + Memory + Tools)")
    print("=" * 60)
    agent = StudyAssistantAgent()
    print(agent._handle_topics())
    print("\nAsk a question, request a quiz, or ask for a study plan.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        response = agent.handle(user_input)
        print(f"\nAssistant:\n{response}\n")


if __name__ == "__main__":
    main()
