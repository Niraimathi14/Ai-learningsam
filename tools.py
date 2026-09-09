import random
import re


class QuizTool:
    """Generates fill-in-the-blank quiz questions from source sentences."""

    name = "quiz_generator"
    description = "Generate a quiz with N questions for a given topic."

    # Words we prefer to blank out because they tend to be the key term
    _STOPWORDS = {
        "the", "a", "an", "is", "are", "of", "and", "to", "in", "that",
        "it", "as", "for", "on", "with", "by", "or", "at", "be", "this",
        "which", "its", "into", "from", "such", "used", "than",
    }

    def run(self, chunks, num_questions=5):
        random.shuffle(chunks)
        questions = []
        for chunk in chunks:
            if len(questions) >= num_questions:
                break
            words = re.findall(r"[A-Za-z']+", chunk.text)
            candidates = [
                w for w in words
                if len(w) > 4 and w.lower() not in self._STOPWORDS
            ]
            if not candidates:
                continue
            answer = random.choice(candidates)
            # Blank out the first case-insensitive occurrence of the answer
            blanked = re.sub(
                rf"\b{re.escape(answer)}\b", "_____", chunk.text, count=1,
                flags=re.IGNORECASE,
            )
            if "_____" not in blanked:
                continue
            questions.append({
                "question": blanked,
                "answer": answer,
                "source": chunk.source,
            })
        return questions


class LearningPlanTool:
    """Builds a day-by-day study plan from retrieved topic chunks."""

    name = "learning_plan_generator"
    description = "Create a day-by-day study plan for a given topic."

    def run(self, topic, chunks, days=5):
        if not chunks:
            return []

        # Distribute concept sentences evenly across the requested days
        buckets = [[] for _ in range(days)]
        for i, chunk in enumerate(chunks):
            buckets[i % days].append(chunk.text)

        plan = []
        for day_num, bucket in enumerate(buckets, start=1):
            if not bucket:
                continue
            focus = bucket[0]
            plan.append({
                "day": day_num,
                "focus_concepts": bucket,
                "goal": f"Understand and practice: {focus}",
            })
        return plan
