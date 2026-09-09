from agent import StudyAssistantAgent


def banner(title):
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)


def main():
    agent = StudyAssistantAgent()

    banner("Available topics")
    print(agent._handle_topics())

    banner("Q&A via RAG: 'What is a binary search tree?'")
    print(agent.handle("What is a binary search tree?"))

    banner("Q&A via RAG: 'How does merge sort work?'")
    print(agent.handle("How does merge sort work?"))

    banner("Tool: Quiz on Algorithms")
    print(agent.handle("Give me a quiz on Algorithms"))

    banner("Tool: 3-day learning plan for Data Structures")
    print(agent.handle("Create a 3 day plan for Data Structures"))

    banner("Memory: learner progress so far")
    print(agent.handle("What is my progress?"))


if __name__ == "__main__":
    main()
