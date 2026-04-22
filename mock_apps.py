"""Mock enterprise applications with APIs.

Simulates Gmail, Slack, Jira, HRIS, CRM, and deployment systems.
Every API call has a verifiable response — this is what makes rewards OBJECTIVE.
"""

from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime


class EnterpriseApps:
    """Simulated enterprise app ecosystem with verifiable API state."""

    def __init__(self):
        self.reset()

    def reset(self):
        # Gmail state
        self.gmail = {
            "accounts": {},  # email -> {created_at, active}
            "sent_emails": [],  # list of {to, subject, body, sent_at}
        }
        # Slack state
        self.slack = {
            "users": {},  # user_id -> {channels, created_at}
            "messages": [],  # list of {channel, user, text}
            "channels": ["#general", "#engineering", "#sales", "#support", "#hr"],
        }
        # Jira state
        self.jira = {
            "tickets": {},  # ticket_id -> {title, status, assignee, priority, type}
            "sprints": {"SPRINT-1": {"status": "active", "tickets": []}},
        }
        # HRIS state
        self.hris = {
            "employees": {},  # emp_id -> {name, email, dept, start_date, equipment}
        }
        # CRM state
        self.crm = {
            "customers": {},  # cust_id -> {name, status, tier, last_contact}
            "tickets": {},  # ticket_id -> {customer, issue, status, assignee}
        }
        # Deployment state
        self.deploy = {
            "services": {"api": "v1.0.0", "web": "v1.0.0", "worker": "v1.0.0"},
            "deployments": [],  # history
            "status_page": "operational",
            "incidents": {},
        }
        # Finance state
        self.finance = {
            "expenses": {},  # exp_id -> {amount, category, status, approver}
            "policy_limits": {
                "travel": 1000,
                "meals": 100,
                "equipment": 2000,
                "training": 5000,
            },
        }
        # Audit log
        self.audit_log = []

    # ── Gmail APIs ───────────────────────────────────────────────────────
    def gmail_create_account(self, email: str) -> Dict:
        if not email or "@" not in email:
            return {"success": False, "error": "Invalid email"}
        if email in self.gmail["accounts"]:
            return {"success": False, "error": "Email already exists"}
        self.gmail["accounts"][email] = {"created_at": "now", "active": True}
        self._log(f"gmail.create_account({email})")
        return {"success": True, "email": email}

    def gmail_send_email(self, to: str, subject: str, body: str) -> Dict:
        if not to or not subject:
            return {"success": False, "error": "Missing required fields"}
        email_id = f"email_{len(self.gmail['sent_emails'])+1}"
        self.gmail["sent_emails"].append({
            "id": email_id, "to": to, "subject": subject, "body": body, "sent_at": "now"
        })
        self._log(f"gmail.send_email(to={to}, subject={subject})")
        return {"success": True, "email_id": email_id}

    # ── Slack APIs ───────────────────────────────────────────────────────
    def slack_add_user(self, user_id: str, channels: List[str]) -> Dict:
        if not user_id:
            return {"success": False, "error": "user_id required"}
        invalid = [c for c in channels if c not in self.slack["channels"]]
        if invalid:
            return {"success": False, "error": f"Invalid channels: {invalid}"}
        self.slack["users"][user_id] = {"channels": channels, "created_at": "now"}
        self._log(f"slack.add_user({user_id}, channels={channels})")
        return {"success": True, "user_id": user_id, "channels": channels}

    def slack_send_message(self, channel: str, text: str) -> Dict:
        if channel not in self.slack["channels"]:
            return {"success": False, "error": f"Channel {channel} not found"}
        if not text:
            return {"success": False, "error": "Message text required"}
        msg = {"channel": channel, "text": text, "id": f"msg_{len(self.slack['messages'])+1}"}
        self.slack["messages"].append(msg)
        self._log(f"slack.send_message(channel={channel})")
        return {"success": True, "message_id": msg["id"]}

    # ── Jira APIs ────────────────────────────────────────────────────────
    def jira_create_ticket(self, title: str, ticket_type: str, priority: str, assignee: str = None) -> Dict:
        valid_types = ["bug", "feature", "task", "incident", "story"]
        valid_priorities = ["low", "medium", "high", "critical", "p0"]
        if ticket_type not in valid_types:
            return {"success": False, "error": f"Invalid type. Must be one of {valid_types}"}
        if priority not in valid_priorities:
            return {"success": False, "error": f"Invalid priority"}
        tid = f"JIRA-{len(self.jira['tickets'])+1}"
        self.jira["tickets"][tid] = {
            "title": title, "type": ticket_type, "priority": priority,
            "assignee": assignee, "status": "open",
        }
        self._log(f"jira.create_ticket(id={tid}, type={ticket_type}, priority={priority})")
        return {"success": True, "ticket_id": tid}

    def jira_update_ticket(self, ticket_id: str, status: str = None, assignee: str = None) -> Dict:
        if ticket_id not in self.jira["tickets"]:
            return {"success": False, "error": "Ticket not found"}
        if status:
            self.jira["tickets"][ticket_id]["status"] = status
        if assignee:
            self.jira["tickets"][ticket_id]["assignee"] = assignee
        self._log(f"jira.update_ticket({ticket_id})")
        return {"success": True, "ticket": self.jira["tickets"][ticket_id]}

    def jira_close_sprint(self, sprint_id: str) -> Dict:
        if sprint_id not in self.jira["sprints"]:
            return {"success": False, "error": "Sprint not found"}
        self.jira["sprints"][sprint_id]["status"] = "closed"
        self._log(f"jira.close_sprint({sprint_id})")
        return {"success": True}

    # ── HRIS APIs ────────────────────────────────────────────────────────
    def hris_create_employee(self, emp_id: str, name: str, email: str, dept: str, start_date: str) -> Dict:
        valid_depts = ["engineering", "sales", "marketing", "hr", "finance", "support", "operations"]
        if dept not in valid_depts:
            return {"success": False, "error": f"Invalid department. Must be one of {valid_depts}"}
        if emp_id in self.hris["employees"]:
            return {"success": False, "error": "Employee ID exists"}
        self.hris["employees"][emp_id] = {
            "name": name, "email": email, "dept": dept,
            "start_date": start_date, "equipment": [],
        }
        self._log(f"hris.create_employee({emp_id}, dept={dept})")
        return {"success": True, "employee_id": emp_id}

    def hris_assign_equipment(self, emp_id: str, equipment: List[str]) -> Dict:
        if emp_id not in self.hris["employees"]:
            return {"success": False, "error": "Employee not found"}
        self.hris["employees"][emp_id]["equipment"] = equipment
        self._log(f"hris.assign_equipment({emp_id}, {equipment})")
        return {"success": True}

    # ── CRM APIs ─────────────────────────────────────────────────────────
    def crm_update_customer(self, customer_id: str, status: str = None, tier: str = None) -> Dict:
        if customer_id not in self.crm["customers"]:
            self.crm["customers"][customer_id] = {
                "status": "active", "tier": "standard", "last_contact": "now"
            }
        if status:
            self.crm["customers"][customer_id]["status"] = status
        if tier:
            self.crm["customers"][customer_id]["tier"] = tier
        self.crm["customers"][customer_id]["last_contact"] = "now"
        self._log(f"crm.update_customer({customer_id})")
        return {"success": True}

    def crm_create_support_ticket(self, customer_id: str, issue: str, assignee: str) -> Dict:
        tid = f"CRM-{len(self.crm['tickets'])+1}"
        self.crm["tickets"][tid] = {
            "customer": customer_id, "issue": issue,
            "status": "open", "assignee": assignee,
        }
        self._log(f"crm.create_support_ticket({tid})")
        return {"success": True, "ticket_id": tid}

    # ── Deployment APIs ──────────────────────────────────────────────────
    def deploy_service(self, service: str, version: str) -> Dict:
        if service not in self.deploy["services"]:
            return {"success": False, "error": f"Service {service} not found"}
        old_version = self.deploy["services"][service]
        self.deploy["services"][service] = version
        self.deploy["deployments"].append({
            "service": service, "from": old_version, "to": version, "at": "now"
        })
        self._log(f"deploy.service({service}, {version})")
        return {"success": True, "deployed": service, "version": version}

    def deploy_rollback(self, service: str) -> Dict:
        if service not in self.deploy["services"]:
            return {"success": False, "error": f"Service {service} not found"}
        # Find last deployment
        history = [d for d in self.deploy["deployments"] if d["service"] == service]
        if not history:
            return {"success": False, "error": "No deployment history"}
        last = history[-1]
        self.deploy["services"][service] = last["from"]
        self._log(f"deploy.rollback({service})")
        return {"success": True, "rolled_back_to": last["from"]}

    def deploy_update_status_page(self, status: str) -> Dict:
        valid = ["operational", "degraded", "partial_outage", "major_outage"]
        if status not in valid:
            return {"success": False, "error": f"Invalid status. Must be one of {valid}"}
        self.deploy["status_page"] = status
        self._log(f"deploy.update_status_page({status})")
        return {"success": True}

    # ── Finance APIs ─────────────────────────────────────────────────────
    def finance_submit_expense(self, emp_id: str, amount: float, category: str, description: str) -> Dict:
        if category not in self.finance["policy_limits"]:
            return {"success": False, "error": f"Invalid category"}
        exp_id = f"EXP-{len(self.finance['expenses'])+1}"
        limit = self.finance["policy_limits"][category]
        status = "auto_approved" if amount <= limit else "pending_approval"
        self.finance["expenses"][exp_id] = {
            "employee": emp_id, "amount": amount, "category": category,
            "description": description, "status": status, "approver": None,
        }
        self._log(f"finance.submit_expense({exp_id}, ${amount}, {category})")
        return {"success": True, "expense_id": exp_id, "status": status, "policy_limit": limit}

    def finance_approve_expense(self, expense_id: str, approver: str) -> Dict:
        if expense_id not in self.finance["expenses"]:
            return {"success": False, "error": "Expense not found"}
        self.finance["expenses"][expense_id]["status"] = "approved"
        self.finance["expenses"][expense_id]["approver"] = approver
        self._log(f"finance.approve_expense({expense_id})")
        return {"success": True}

    # ── Audit helpers ────────────────────────────────────────────────────
    def _log(self, entry: str):
        self.audit_log.append(entry)

    def get_audit_log(self) -> List[str]:
        return self.audit_log

    def get_state_snapshot(self) -> Dict:
        return {
            "gmail_accounts": list(self.gmail["accounts"].keys()),
            "gmail_emails_sent": len(self.gmail["sent_emails"]),
            "slack_users": list(self.slack["users"].keys()),
            "slack_messages": len(self.slack["messages"]),
            "jira_tickets": list(self.jira["tickets"].keys()),
            "hris_employees": list(self.hris["employees"].keys()),
            "crm_customers": list(self.crm["customers"].keys()),
            "crm_tickets": list(self.crm["tickets"].keys()),
            "deploy_services": dict(self.deploy["services"]),
            "deploy_status_page": self.deploy["status_page"],
            "finance_expenses": list(self.finance["expenses"].keys()),
        }
