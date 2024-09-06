from openai import OpenAI
import time
from pydantic import BaseModel
import json


from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    ESSAY = "essay"
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    MATCHING = "matching"
    ORDERING = "ordering"
    NUMERIC = "numeric"
    OTHER = "other"


from typing import Dict


class InLanguage(BaseModel):
    in_english: str
    in_tamil: str


class Question(BaseModel):
    id: int
    question: InLanguage
    type: str
    difficulty: str


class Answer(BaseModel):
    id: int
    question_id: int
    answer: str
    correctness_score: float
    feedback: InLanguage


client = OpenAI()


QUESTION_GENERATOR_ASSISTANT_TEXT = "asst_HXnJ6h5oipLiLHU04GyTJSUs"
QUESTION_GENERATOR_ASSISTANT_JSON = "asst_AwfV1y4BPFoPHWkAsKra2FrH"


ANSWER_GRADER_ASSISTANT_TEXT = "asst_32M6zwui4sQtARgXkD1fQOxt"
ANSWER_GRADER_ASSISTANT_JSON = "asst_REfg4gEqX3oxC3bcBZ1ra6zk"


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def fetch_question(topic, threadId):
    assistant_text = client.beta.assistants.retrieve(QUESTION_GENERATOR_ASSISTANT_TEXT)
    assistant_JSON = client.beta.assistants.retrieve(QUESTION_GENERATOR_ASSISTANT_JSON)

    thread = client.beta.threads.retrieve(thread_id=threadId)

    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Generate a question based on the topic: {topic}",
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_text.id,
    )
    run = wait_on_run(run, thread)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_JSON.id,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Question",
                "schema": Question.schema(),
                "description": "A question generated by the AI assistant",
            },
        },
    )
    run = wait_on_run(run, thread)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    print("messages")
    print(messages)
    question_str = messages.data[0].content[0].text.value
    question = json.loads(question_str)
    res = Question(
        id=int(question["id"]),
        question=question["question"],
        type=question["type"],
        difficulty=question["difficulty"],
    )
    return res


def grade_answer(answer, threadId):
    assistant_text = client.beta.assistants.retrieve(ANSWER_GRADER_ASSISTANT_TEXT)
    assistant_json = client.beta.assistants.retrieve(ANSWER_GRADER_ASSISTANT_JSON)

    thread = client.beta.threads.retrieve(thread_id=threadId)
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=f"Grade the answer: {answer}"
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_text.id,
    )
    run = wait_on_run(run, thread)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_json.id,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Answer",
                "schema": Answer.schema(),
                "description": "An answer graded by the AI assistant",
            },
        },
    )
    run = wait_on_run(run, thread)

    messages = client.beta.threads.messages.list(thread_id=thread.id)
    feedback_str = messages.data[0].content[0].text.value
    feedback = json.loads(feedback_str)
    res = {
        "id": int(feedback["id"]),
        "question_id": int(feedback["question_id"]),
        "answer": feedback["answer"],
        "score": float(feedback["correctness_score"]),
        "feedback": feedback["feedback"],
    }

    score = float(feedback["correctness_score"])
    feedback = feedback["feedback"]
    return score, feedback


def create_thread():
    thread = client.beta.threads.create()
    print("thread created")
    print(thread)
    return thread
