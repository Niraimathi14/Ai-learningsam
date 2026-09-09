import json
import os
from datetime import datetime


class Memory:
    def __init__(self, storage_path="data/learner_memory.json", max_turns=10):
        self.storage_path = storage_path
        self.max_turns = max_turns
        self.conversation = []  # short-term, in-RAM
        self.state = {
            "topics_studied": [],
            "quiz_history": [],
            "learning_plans": [],
        }
        self._load()

    # ---------- persistence ----------
    def _load(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

    def _save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2)

    # ---------- short-term conversation memory ----------
    def add_turn(self, role, content):
        self.conversation.append({"role": role, "content": content})
        if len(self.conversation) > self.max_turns:
            self.conversation.pop(0)

    def recent_context(self):
        return self.conversation[-self.max_turns:]

    # ---------- long-term learner memory ----------
    def record_topic_studied(self, topic):
        entry = {"topic": topic, "timestamp": datetime.now().isoformat()}
        self.state["topics_studied"].append(entry)
        self._save()

    def record_quiz_result(self, topic, score, total):
        entry = {
            "topic": topic,
            "score": score,
            "total": total,
            "timestamp": datetime.now().isoformat(),
        }
        self.state["quiz_history"].append(entry)
        self._save()

    def record_learning_plan(self, topic, days, plan):
        entry = {
            "topic": topic,
            "days": days,
            "plan": plan,
            "timestamp": datetime.now().isoformat(),
        }
        self.state["learning_plans"].append(entry)
        self._save()

    def summary(self):
        topics = {t["topic"] for t in self.state["topics_studied"]}
        quizzes = len(self.state["quiz_history"])
        plans = len(self.state["learning_plans"])
        return (
            f"Topics studied: {len(topics)} ({', '.join(sorted(topics)) or 'none yet'})\n"
            f"Quizzes taken: {quizzes}\n"
            f"Learning plans created: {plans}"
        )
