"""Baseline inference script for WorkFlow Arena."""

import os
import time
import json
import subprocess
import socket
from typing import Dict, List

import httpx
from openai import OpenAI

API_BASE_URL = os.environ["API_BASE_URL"]
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.environ["API_KEY"]

LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
ENV_URL = os.getenv("ENV_URL", "https://jaydeepshah2025-workflow-arena.hf.space")

BENCHMARK = "workflow-arena"
TASK_NAMES = ["employee_onboarding", "customer_support", "expense_approval", "sprint_release", "incident_response"]
MAX_STEPS = 15
MAX_TOTAL_REWARD = 1.0
SUCCESS_SCORE_THRESHOLD = 0.5


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step, action, reward, done, error=None):
    a = str(action).replace("\n", " ")[:500]
    print(f"[STEP] step={step} action={a} reward={reward:.2f} done={'true' if done else 'false'} error={error or 'null'}", flush=True)


def log_end(success, steps, score, rewards):
    rstr = ",".join(f"{r:.2f}" for r in rewards) if rewards else "0.00"
    safe_score = max(0.01, min(0.99, float(score)))
    print(f"[END] success={'true' if success else 'false'} steps={steps} score={safe_score:.2f} rewards={rstr}", flush=True)


SYSTEM_PROMPT = """\
You are an enterprise AI agent that orchestrates multi-app business workflows. You must \
execute API calls across Gmail, Slack, Jira, HRIS, CRM, Deploy, and Finance systems.

Respond with ONLY a JSON object:
{
  "calls": [
    {
      "app": "gmail|slack|jira|hris|crm|deploy|finance",
      "method": "<method_name>",
      "params": {"key": "value"},
      "reasoning": "<explain WHY this call is needed>"
    }
  ]
}

Available APIs:
- gmail.create_account(email), gmail.send_email(to, subject, body)
- slack.add_user(user_id, channels), slack.send_message(channel, text)
- jira.create_ticket(title, ticket_type, priority, assignee), jira.update_ticket(ticket_id, status)
- jira.close_sprint(sprint_id)
- hris.create_employee(emp_id, name, email, dept, start_date), hris.assign_equipment(emp_id, equipment)
- crm.update_customer(customer_id, status, tier), crm.create_support_ticket(customer_id, issue, assignee)
- deploy.service(service, version), deploy.rollback(service), deploy.update_status_page(status)
- finance.submit_expense(emp_id, amount, category, description), finance.approve_expense(expense_id, approver)

Complete the workflow by making the correct API calls in the right priority order."""


def get_model_response(client, observation, last_reward, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for h in history[-2:]:
        messages.append({"role": "assistant", "content": h["action"]})
        messages.append({"role": "user", "content": h["feedback"]})
    user_msg = observation
    if last_reward and history:
        user_msg = f"Previous score: {last_reward:+.3f}. Continue the workflow.\n\n" + observation
    messages.append({"role": "user", "content": user_msg})
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME, messages=messages,
            temperature=0.1, max_completion_tokens=2000
        )
        return resp.choices[0].message.content
    except Exception as exc:
        print(f"[DEBUG] LLM error: {exc}", flush=True)
        return '{"calls": []}'


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def start_container(image, port):
    return subprocess.Popen(["docker", "run", "--rm", "-p", f"{port}:7860", image],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def wait_for_server(url, retries=60, delay=2.0):
    for i in range(retries):
        try:
            if httpx.get(f"{url}/health", timeout=5.0).status_code == 200:
                print(f"[DEBUG] Server ready at {url}", flush=True)
                return True
        except Exception:
            pass
        time.sleep(delay)
    return False


def run_task(llm, http, base_url, task_name):
    rewards = []
    steps_taken = 0
    score = 0.0
    success = False
    history = []

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        reset = http.post(f"{base_url}/reset", json={"task_name": task_name}).json()
        session_id = reset["session_id"]
        observation = reset["observation"]["content"]
        done = reset.get("done", False)
        last_reward = 0.0

        for step in range(1, MAX_STEPS + 1):
            if done:
                break
            action = get_model_response(llm, observation, last_reward, history)
            step_data = http.post(f"{base_url}/step",
                                  json={"session_id": session_id, "message": action}).json()

            reward = float(step_data.get("reward", 0) or 0)
            done = step_data.get("done", False)
            observation = step_data["observation"]["content"]

            rewards.append(reward)
            steps_taken = step
            last_reward = reward
            history.append({"action": action, "feedback": observation})

            log_step(step=step, action=action, reward=reward, done=done, error=None)

            if done:
                break

        score = sum(rewards) / MAX_TOTAL_REWARD if MAX_TOTAL_REWARD > 0 else 0.0
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD
    except Exception as exc:
        print(f"[DEBUG] Task {task_name} error: {exc}", flush=True)

    if score <= 0.0:
        score = 0.01
    if score >= 1.0:
        score = 0.99

    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return score


def main():
    print(f"[DEBUG] ENV_URL={ENV_URL}", flush=True)
    print(f"[DEBUG] MODEL_NAME={MODEL_NAME}", flush=True)

    llm = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    container = None
    base_url = ENV_URL

    try:
        if LOCAL_IMAGE_NAME:
            port = find_free_port()
            container = start_container(LOCAL_IMAGE_NAME, port)
            base_url = f"http://localhost:{port}"

        if not wait_for_server(base_url):
            print("[DEBUG] Server not reachable", flush=True)

        with httpx.Client(timeout=120.0) as http:
            for task in TASK_NAMES:
                s = run_task(llm, http, base_url, task)
                print(f"[DEBUG] {task}: {s:.3f}", flush=True)
    finally:
        if container:
            container.terminate()
            try:
                container.wait(timeout=10)
            except Exception:
                container.kill()


if __name__ == "__main__":
    main()
