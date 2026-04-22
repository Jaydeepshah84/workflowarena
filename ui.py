"""Gradio UI for WorkFlow Arena."""

import gradio as gr
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from server.environment import WorkFlowEnvironment
from workflows import WORKFLOWS

ui_env = None
ui_history = []


def reset_env(task_name):
    global ui_env, ui_history
    ui_env = WorkFlowEnvironment()
    result = ui_env.reset(task_name)
    ui_history = []
    observation = result["observation"]["content"]
    info = result["info"]
    status = (
        f"**Workflow:** {info['task_name']}\n\n"
        f"**Required Actions:** {info['total_required_actions']}\n\n"
        f"**Status:** Ready"
    )
    return observation, status, "", "0.00", f"0 / {info['total_required_actions']}", ""


def step_env(action_text):
    global ui_env, ui_history
    if ui_env is None:
        return "Reset the environment first!", "", "", "", "", ""

    result = ui_env.step(action_text)
    observation = result["observation"]["content"]
    reward = result["reward"]
    done = result["done"]
    info = result["info"]

    ui_history.append(reward)
    reward_chart = "**Reward per step:**\n\n"
    for i, r in enumerate(ui_history):
        bar = "█" * int(r * 40)
        reward_chart += f"Step {i+1}: {bar} {r:.3f}\n\n"

    score = f"{info['cumulative_score']:.2f}"
    progress = f"{info['completed_actions']} / {info['total_required_actions']}"

    api_stats = (
        f"**API Calls Made:** {info['api_calls_made']}\n\n"
        f"**API Success Rate:** {info['api_calls_successful']}/{info['api_calls_made']}\n\n"
        f"**Completed Actions:** {info['completed_actions']}/{info['total_required_actions']}"
    )

    status = f"**Step:** {ui_env.step_count}/{ui_env.max_steps}\n\n**Done:** {done}"
    if done:
        status += "\n\n**WORKFLOW COMPLETE**"

    return observation, status, reward_chart, score, progress, api_stats


def create_sample_action(task_name):
    samples = {
        "employee_onboarding": {
            "calls": [
                {"app": "gmail", "method": "create_account",
                 "params": {"email": "alice.johnson@company.com"},
                 "reasoning": "Step 1: Create email account for new employee"},
                {"app": "hris", "method": "create_employee",
                 "params": {"emp_id": "E1001", "name": "Alice Johnson",
                            "email": "alice.johnson@company.com",
                            "dept": "engineering", "start_date": "2026-04-28"},
                 "reasoning": "Step 2: Create HRIS record for engineering dept"},
            ]
        },
        "customer_support": {
            "calls": [
                {"app": "crm", "method": "create_support_ticket",
                 "params": {"customer_id": "C2050", "issue": "API 500 errors",
                            "assignee": "support_team"},
                 "reasoning": "Create CRM ticket for enterprise customer issue"},
                {"app": "jira", "method": "create_ticket",
                 "params": {"title": "API 500 errors", "ticket_type": "bug",
                            "priority": "high"},
                 "reasoning": "Escalate to engineering with high priority bug"},
            ]
        },
        "expense_approval": {
            "calls": [
                {"app": "finance", "method": "submit_expense",
                 "params": {"emp_id": "E1001", "amount": 85,
                            "category": "meals", "description": "Client dinner"},
                 "reasoning": "Under $100 meal limit — should auto-approve"},
            ]
        },
        "sprint_release": {
            "calls": [
                {"app": "slack", "method": "send_message",
                 "params": {"channel": "#engineering",
                            "text": "Starting release v1.1.0 deployment"},
                 "reasoning": "Notify team before release begins"},
                {"app": "deploy", "method": "update_status_page",
                 "params": {"status": "degraded"},
                 "reasoning": "Set status to degraded during deployment"},
            ]
        },
        "incident_response": {
            "calls": [
                {"app": "jira", "method": "create_ticket",
                 "params": {"title": "P0: API down", "ticket_type": "incident",
                            "priority": "p0"},
                 "reasoning": "Create P0 incident ticket"},
                {"app": "deploy", "method": "rollback",
                 "params": {"service": "api"},
                 "reasoning": "Rollback the broken deployment immediately"},
            ]
        },
    }
    return json.dumps(samples.get(task_name, samples["employee_onboarding"]), indent=2)


with gr.Blocks(title="WorkFlow Arena", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# 🏢 WorkFlow Arena — Multi-App Enterprise Workflow RL Environment\n"
        "**Train AI agents to orchestrate real business workflows across Gmail, Slack, Jira, "
        "HRIS, CRM, and more. Every reward is VERIFIED via actual API responses.**\n\n"
        "Theme 3.1 + Scaler AI Labs Sub-theme"
    )

    with gr.Row():
        with gr.Column(scale=2):
            task_dropdown = gr.Dropdown(
                choices=list(WORKFLOWS.keys()),
                value="employee_onboarding",
                label="Select Workflow",
            )
            with gr.Row():
                reset_btn = gr.Button("🔄 Reset", variant="primary")
                sample_btn = gr.Button("📋 Sample API Calls")
            action_input = gr.Textbox(
                label="Your API Calls (JSON)",
                placeholder='{"calls": [{"app": "...", "method": "...", "params": {}, "reasoning": "..."}]}',
                lines=10,
            )
            step_btn = gr.Button("▶️ Execute Step", variant="primary")

        with gr.Column(scale=1):
            score_display = gr.Textbox(label="Score", value="0.00", interactive=False)
            progress_display = gr.Textbox(label="Required Actions", value="0 / 0", interactive=False)
            status_display = gr.Markdown(value="Reset to start")
            api_stats_display = gr.Markdown(value="No API calls yet")

    with gr.Row():
        with gr.Column(scale=2):
            observation_display = gr.Textbox(
                label="Observation (Scenario + Feedback + App State)",
                lines=22, interactive=False,
            )
        with gr.Column(scale=1):
            reward_display = gr.Markdown(label="Reward History", value="No steps yet")

    reset_btn.click(fn=reset_env, inputs=[task_dropdown],
                    outputs=[observation_display, status_display, reward_display,
                             score_display, progress_display, api_stats_display])
    step_btn.click(fn=step_env, inputs=[action_input],
                   outputs=[observation_display, status_display, reward_display,
                            score_display, progress_display, api_stats_display])
    sample_btn.click(fn=create_sample_action, inputs=[task_dropdown], outputs=[action_input])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
