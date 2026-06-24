"""
recommendations.py
Phase 4: Turn statistical findings into prioritised, plain-English actions.

The rule: a recommendation ONLY exists if a real finding caused it.
No finding, no recommendation. Every action traces back to evidence.
"""

# Maps a finding (by the columns it involves) to a recommendation.
# Each entry: a plain-English action + a priority weight (higher = more urgent).
RECOMMENDATION_RULES = {
    ("Response Hours", "CSAT Score"): {
        "action": "Reduce response times. Satisfaction falls as customers wait longer, "
                  "so faster first responses should directly lift CSAT.",
        "priority": 100,
    },
    ("CSAT Score", "Agent Tenure"): {
        "action": "Invest in training and support for newer agents. Satisfaction varies "
                  "by agent experience, so onboarding and mentoring should raise scores.",
        "priority": 80,
    },
    ("CSAT Score", "Agent Shift"): {
        "action": "Review staffing and support quality on lower-scoring shifts. "
                  "Satisfaction depends on which shift handles the ticket.",
        "priority": 70,
    },
    ("CSAT Score", "Category"): {
        "action": "Prioritise the complaint categories with the lowest satisfaction. "
                  "Some issue types leave customers far less happy than others.",
        "priority": 60,
    },
    ("Response Hours", "Category"): {
        "action": "Investigate the slowest complaint categories. Some issue types take "
                  "much longer to respond to and may need dedicated handling.",
        "priority": 50,
    },
    ("Category", "Channel"): {
        "action": "Align channel resourcing with the issue types each channel attracts, "
                  "since complaint mix differs significantly by channel.",
        "priority": 30,
    },
    ("Category", "Agent Shift"): {
        "action": "Match agent skills to shifts based on the complaint mix each shift sees.",
        "priority": 20,
    },
    ("Category", "Agent Tenure"): {
        "action": "Route complex complaint categories toward more experienced agents.",
        "priority": 20,
    },
}


def _key_for(finding):
    """Find which rule matches a finding, regardless of column order."""
    text = finding["finding"]
    for (a, b), rule in RECOMMENDATION_RULES.items():
        if a in text and b in text:
            return rule
    return None


def generate_recommendations(findings):
    """
    Take the list of findings from the statistics engine and produce
    prioritised recommendations. Only significant findings count.
    """
    recs = []
    for f in findings:
        if not f["significant"]:
            continue
        rule = _key_for(f)
        if rule is None:
            continue
        recs.append({
            "action": rule["action"],
            "priority": rule["priority"],
            "evidence": f["finding"],
            "test": f["test"],
            "p_value": f["p_value"],
        })

    # Highest priority first.
    recs.sort(key=lambda r: r["priority"], reverse=True)
    return recs


if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from load_data import load_tickets, clean_tickets
    from statistics_engine import run_all_tests

    raw = load_tickets()
    all_tickets, rated_tickets = clean_tickets(raw)
    findings = run_all_tests(all_tickets, rated_tickets)

    recs = generate_recommendations(findings)

    print(f"Generated {len(recs)} prioritised recommendations:\n")
    for i, r in enumerate(recs, 1):
        print(f"{i}. {r['action']}")
        print(f"   Evidence: {r['evidence']}")
        print()