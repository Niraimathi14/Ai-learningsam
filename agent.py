import re

from rag import RAGIndex
from memory import Memory
from tools import QuizTool, LearningPlanTool


class StudyAssistantAgent:
    def __init__(self, corpus_dir="data/course_materials", memory_path="data/learner_memory.json"):
        self.rag = RAGIndex(corpus_dir=corpus_dir)
        self.memory = Memory(storage_path=memory_path)
        self.quiz_tool = QuizTool()
        self.plan_tool = LearningPlanTool()

    # ---------- intent routing ----------
    def handle(self, user_input):
        self.memory.add_turn("user", user_input)
        text = user_input.lower().strip()

        if re.search(r"\bquiz\b|\btest me\b", text):
            response = self._handle_quiz(user_input)
        elif re.search(r"\bplan\b|\bschedule\b|\bstudy plan\b", text):
            response = self._handle_plan(user_input)
        elif re.search(r"\bprogress\b|\bmy stats\b|\bhow am i doing\b", text):
            response = self._handle_progress()
        elif re.search(r"\btopics\b|\bwhat can (i|you) study\b|\bavailable\b", text):
            response = self._handle_topics()
        else:
            response = self._handle_question(user_input)

        self.memory.add_turn("assistant", response)
        return response

    # ---------- capability: RAG + Memory (Q&A) ----------
    def _handle_question(self, query):
        chunks = self.rag.retrieve(query, top_k=4)
        if not chunks:
            return ("I couldn't find anything relevant to that in the course "
                     "materials. Try asking about Python basics, data "
                     "structures, or algorithms.")

        topic = chunks[0].topic
        self.memory.record_topic_studied(topic)

        answer_lines = [f"Based on the course materials on '{topic}':"]
        for c in chunks:
            answer_lines.append(f" - {c.text}")
        answer_lines.append(
            f"\n(Retrieved {len(chunks)} relevant passage(s) via RAG; "
            f"remembered that you studied '{topic}'.)"
        )
        return "\n".join(answer_lines)

    # ---------- capability: Tools (quiz) ----------
    def _handle_quiz(self, query):
        topic = self._extract_topic(query)
        chunks = (self.rag.chunks_for_topic(topic) if topic
                  else self.rag.retrieve(query, top_k=10))
        if not chunks:
            return f"I don't have material to quiz you on '{topic or query}' yet."

        questions = self.quiz_tool.run(chunks, num_questions=5)
        if not questions:
            return "I couldn't generate quiz questions from that topic."

        lines = [f"Quiz: {topic or 'General'} ({len(questions)} questions)"]
        for i, q in enumerate(questions, start=1):
            lines.append(f" {i}. {q['question']}")
        lines.append(
            "\n(Answers stored internally. Tell me your answers and I can "
            "score them, e.g. 'my answers are: list, tuple, class, ...')"
        )

        # Stash answer key + last quiz topic in memory for later scoring
        self._last_quiz = {"topic": topic or "general", "questions": questions}
        return "\n".join(lines)

    def score_quiz(self, answers_text):
        """Optional helper: score the most recent quiz against free-text answers."""
        if not hasattr(self, "_last_quiz"):
            return "There's no active quiz to score. Ask for a quiz first."
        given = [a.strip().lower() for a in re.split(r",|\n", answers_text) if a.strip()]
        questions = self._last_quiz["questions"]
        correct = 0
        for i, q in enumerate(questions):
            if i < len(given) and given[i] == q["answer"].lower():
                correct += 1
        self.memory.record_quiz_result(self._last_quiz["topic"], correct, len(questions))
        return f"You scored {correct}/{len(questions)} on the {self._last_quiz['topic']} quiz."

    # ---------- capability: Tools (learning plan) ----------
    def _handle_plan(self, query):
        topic = self._extract_topic(query)
        days_match = re.search(r"(\d+)\s*day", query.lower())
        days = int(days_match.group(1)) if days_match else 5

        chunks = (self.rag.chunks_for_topic(topic) if topic
                  else self.rag.retrieve(query, top_k=days * 3))
        if not chunks:
            return f"I don't have material to build a plan for '{topic or query}' yet."

        plan = self.plan_tool.run(topic or query, chunks, days=days)
        self.memory.record_learning_plan(topic or query, days, plan)

        lines = [f"{days}-Day Learning Plan: {topic or query}"]
        for day in plan:
            lines.append(f" Day {day['day']}: {day['goal']}")
            for concept in day["focus_concepts"][1:]:
                lines.append(f" - Also review: {concept}")
        return "\n".join(lines)

    # ---------- capability: Memory (progress) ----------
    def _handle_progress(self):
        return self.memory.summary()

    def _handle_topics(self):
        return "Available topics: " + ", ".join(self.rag.topics())

    # ---------- helpers ----------
    def _extract_topic(self, text):
        text_low = text.lower()
        for topic in self.rag.topics():
            if topic.lower() in text_low:
                return topic
        return None
