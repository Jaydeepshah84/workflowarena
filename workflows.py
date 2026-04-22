"""Enterprise workflow definitions for WorkFlow Arena.

Each workflow is a multi-step business process that requires the agent
to orchestrate actions across multiple apps (Gmail, Slack, Jira, HRIS, CRM, etc.).

Every step has VERIFIABLE SUCCESS CRITERIA — no subjective judgment.
"""

WORKFLOWS = {
    # ── WORKFLOW 1: Employee Onboarding (Easy) ──────────────────────────
    "employee_onboarding": {
        "name": "Employee Onboarding",
        "difficulty": "easy",
        "description": (
            "New engineering hire Alice Johnson starts Monday. "
            "Complete her onboarding across 5 apps. Every action must succeed."
        ),
        "max_steps": 12,
        "scenario": {
            "new_employee": {
                "name": "Alice Johnson",
                "email": "alice.johnson@company.com",
                "emp_id": "E1001",
                "dept": "engineering",
                "start_date": "2026-04-28",
                "role": "Senior Software Engineer",
            },
            "department_config": {
                "engineering": {
                    "slack_channels": ["#general", "#engineering"],
                    "equipment": ["laptop", "monitor", "keyboard"],
                    "welcome_channel": "#engineering",
                },
            },
        },
        "required_actions": [
            {
                "id": "create_email",
                "app": "gmail",
                "method": "create_account",
                "params": {"email": "alice.johnson@company.com"},
                "priority": 1,
            },
            {
                "id": "create_hris",
                "app": "hris",
                "method": "create_employee",
                "params": {
                    "emp_id": "E1001", "name": "Alice Johnson",
                    "email": "alice.johnson@company.com",
                    "dept": "engineering", "start_date": "2026-04-28",
                },
                "priority": 2,
            },
            {
                "id": "slack_access",
                "app": "slack",
                "method": "add_user",
                "params": {
                    "user_id": "alice.johnson",
                    "channels": ["#general", "#engineering"],
                },
                "priority": 3,
            },
            {
                "id": "assign_equipment",
                "app": "hris",
                "method": "assign_equipment",
                "params": {
                    "emp_id": "E1001",
                    "equipment": ["laptop", "monitor", "keyboard"],
                },
                "priority": 4,
            },
            {
                "id": "welcome_email",
                "app": "gmail",
                "method": "send_email",
                "params": {
                    "to": "alice.johnson@company.com",
                    "subject_contains": "welcome",
                },
                "priority": 5,
            },
            {
                "id": "team_announcement",
                "app": "slack",
                "method": "send_message",
                "params": {
                    "channel": "#engineering",
                    "text_contains": "alice",
                },
                "priority": 6,
            },
        ],
    },

    # ── WORKFLOW 2: Customer Support Triage (Easy-Medium) ───────────────
    "customer_support": {
        "name": "Customer Support Triage",
        "difficulty": "medium",
        "description": (
            "High-priority customer (Enterprise tier) reports a critical issue. "
            "Triage, escalate, and resolve the workflow across Jira, CRM, and Slack."
        ),
        "max_steps": 12,
        "scenario": {
            "customer": {
                "id": "C2050",
                "name": "Acme Corp",
                "tier": "enterprise",
                "status": "active",
            },
            "incident": {
                "issue": "API returning 500 errors for bulk operations",
                "severity": "high",
                "affected_users": 500,
            },
        },
        "required_actions": [
            {
                "id": "create_crm_ticket",
                "app": "crm",
                "method": "create_support_ticket",
                "params": {
                    "customer_id": "C2050",
                    "assignee": "support_team",
                },
                "priority": 1,
            },
            {
                "id": "create_jira_bug",
                "app": "jira",
                "method": "create_ticket",
                "params": {
                    "type": "bug",
                    "priority": "high",
                },
                "priority": 2,
            },
            {
                "id": "notify_engineering",
                "app": "slack",
                "method": "send_message",
                "params": {
                    "channel": "#engineering",
                    "text_contains": "critical",
                },
                "priority": 3,
            },
            {
                "id": "notify_customer",
                "app": "gmail",
                "method": "send_email",
                "params": {
                    "subject_contains": "investigating",
                },
                "priority": 4,
            },
            {
                "id": "update_crm_status",
                "app": "crm",
                "method": "update_customer",
                "params": {
                    "customer_id": "C2050",
                    "status": "escalated",
                },
                "priority": 5,
            },
        ],
    },

    # ── WORKFLOW 3: Expense Approval (Medium) ────────────────────────────
    "expense_approval": {
        "name": "Expense Approval Workflow",
        "difficulty": "medium",
        "description": (
            "Process 3 expense submissions. Each must be routed correctly based on "
            "policy limits. Agent must check limits, approve/escalate appropriately."
        ),
        "max_steps": 10,
        "scenario": {
            "expenses": [
                {"emp_id": "E1001", "amount": 85, "category": "meals", "description": "Client dinner"},
                {"emp_id": "E1002", "amount": 1500, "category": "travel", "description": "Conference travel"},
                {"emp_id": "E1003", "amount": 1800, "category": "equipment", "description": "New laptop"},
            ],
            "policy_limits": {
                "meals": 100,  # auto-approve under
                "travel": 1000,  # auto-approve under, else manager approval
                "equipment": 2000,  # under this auto-approved
            },
        },
        "required_actions": [
            {
                "id": "submit_expense_1",
                "app": "finance",
                "method": "submit_expense",
                "params": {"emp_id": "E1001", "category": "meals", "amount": 85},
                "priority": 1,
            },
            {
                "id": "submit_expense_2",
                "app": "finance",
                "method": "submit_expense",
                "params": {"emp_id": "E1002", "category": "travel", "amount": 1500},
                "priority": 2,
            },
            {
                "id": "submit_expense_3",
                "app": "finance",
                "method": "submit_expense",
                "params": {"emp_id": "E1003", "category": "equipment", "amount": 1800},
                "priority": 3,
            },
            {
                "id": "notify_employee_1",
                "app": "gmail",
                "method": "send_email",
                "params": {"subject_contains": "approved"},
                "priority": 4,
            },
            {
                "id": "escalate_travel",
                "app": "slack",
                "method": "send_message",
                "params": {"channel": "#general", "text_contains": "approval"},
                "priority": 5,
            },
        ],
    },

    # ── WORKFLOW 4: Sprint Release (Hard) ────────────────────────────────
    "sprint_release": {
        "name": "Sprint Release Management",
        "difficulty": "hard",
        "description": (
            "Execute a production release: close sprint, deploy services, "
            "update status page, notify stakeholders. Handle rollback if deploy fails."
        ),
        "max_steps": 15,
        "scenario": {
            "sprint": "SPRINT-1",
            "services_to_deploy": ["api", "web"],
            "new_version": "v1.1.0",
            "release_notes": "New features: bulk operations, improved performance",
        },
        "required_actions": [
            {
                "id": "notify_release_start",
                "app": "slack",
                "method": "send_message",
                "params": {"channel": "#engineering", "text_contains": "release"},
                "priority": 1,
            },
            {
                "id": "update_status_maintenance",
                "app": "deploy",
                "method": "update_status_page",
                "params": {"status": "degraded"},
                "priority": 2,
            },
            {
                "id": "deploy_api",
                "app": "deploy",
                "method": "service",
                "params": {"service": "api", "version": "v1.1.0"},
                "priority": 3,
            },
            {
                "id": "deploy_web",
                "app": "deploy",
                "method": "service",
                "params": {"service": "web", "version": "v1.1.0"},
                "priority": 4,
            },
            {
                "id": "close_sprint",
                "app": "jira",
                "method": "close_sprint",
                "params": {"sprint_id": "SPRINT-1"},
                "priority": 5,
            },
            {
                "id": "restore_status",
                "app": "deploy",
                "method": "update_status_page",
                "params": {"status": "operational"},
                "priority": 6,
            },
            {
                "id": "notify_release_complete",
                "app": "gmail",
                "method": "send_email",
                "params": {"subject_contains": "release"},
                "priority": 7,
            },
        ],
    },

    # ── WORKFLOW 5: Incident Response (Expert) ───────────────────────────
    "incident_response": {
        "name": "Production Incident Response",
        "difficulty": "expert",
        "description": (
            "P0 incident: API service crashed. Execute full incident response: "
            "triage, rollback, communication, tracking. Time-critical workflow."
        ),
        "max_steps": 15,
        "scenario": {
            "alert": {
                "service": "api",
                "severity": "p0",
                "error_rate": "100%",
                "started_at": "2 minutes ago",
            },
            "last_deploy": {"service": "api", "version": "v1.1.0", "from": "v1.0.0"},
        },
        "required_actions": [
            {
                "id": "create_incident_ticket",
                "app": "jira",
                "method": "create_ticket",
                "params": {"type": "incident", "priority": "p0"},
                "priority": 1,
            },
            {
                "id": "update_status_outage",
                "app": "deploy",
                "method": "update_status_page",
                "params": {"status": "major_outage"},
                "priority": 2,
            },
            {
                "id": "page_oncall",
                "app": "slack",
                "method": "send_message",
                "params": {"channel": "#engineering", "text_contains": "incident"},
                "priority": 3,
            },
            {
                "id": "rollback_api",
                "app": "deploy",
                "method": "rollback",
                "params": {"service": "api"},
                "priority": 4,
            },
            {
                "id": "notify_stakeholders",
                "app": "gmail",
                "method": "send_email",
                "params": {"subject_contains": "incident"},
                "priority": 5,
            },
            {
                "id": "update_status_operational",
                "app": "deploy",
                "method": "update_status_page",
                "params": {"status": "operational"},
                "priority": 6,
            },
            {
                "id": "notify_customers",
                "app": "crm",
                "method": "update_customer",
                "params": {"status": "notified"},
                "priority": 7,
            },
        ],
    },
}
