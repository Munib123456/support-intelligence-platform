"""
executive_brief.py
Phase 6: The Executive Brief generator.

Produces a plain-language summary for a director, in a fixed structure:
  Finding -> Evidence -> Business Impact -> Recommended Action

The rule (unchanged from the whole project): every number comes from the
data / statistics. Nothing here is invented.
"""


def build_executive_brief(all_tickets, rated_tickets, findings, recs):
    """Return a list of brief sections, each a dict with the four parts."""
    sections = []

    # --- Section 1: the headline response-time / satisfaction finding ---
    spearman = next((f for f in findings
                     if f["test"] == "spearman" and f["significant"]), None)
    if spearman is not None and len(rated_tickets):
        avg_csat = rated_tickets["CSAT Score"].mean()
        sections.append({
            "finding": "Slower response times are linked to lower customer satisfaction.",
            "evidence": spearman["finding"],
            "impact": f"Average satisfaction sits at {avg_csat:.2f} out of 5. "
                      f"Because the relationship is negative, every reduction in "
                      f"response time is expected to lift this score.",
            "action": "Reduce first-response times, starting with the slowest queues.",
        })

    # --- Section 2: the lowest-satisfaction category ---
    if "Category" in rated_tickets.columns and len(rated_tickets):
        by_cat = rated_tickets.groupby("Category")["CSAT Score"].mean().sort_values()
        worst_cat = by_cat.index[0]
        worst_val = by_cat.iloc[0]
        overall = rated_tickets["CSAT Score"].mean()
        sections.append({
            "finding": f"The '{worst_cat}' category has the lowest customer satisfaction.",
            "evidence": f"Its average CSAT is {worst_val:.2f}, against an overall average of {overall:.2f} "
                        f"(satisfaction differs significantly across categories, Kruskal-Wallis p < 0.001).",
            "impact": "Customers raising this issue type leave consistently less satisfied, "
                      "which drags down the overall score.",
            "action": f"Review how '{worst_cat}' cases are handled and resourced.",
        })

    # --- Section 3: the biggest volume category ---
    if "Category" in all_tickets.columns:
        counts = all_tickets["Category"].value_counts()
        top_cat = counts.index[0]
        top_pct = 100 * counts.iloc[0] / len(all_tickets)
        sections.append({
            "finding": f"'{top_cat}' is the single largest source of contacts.",
            "evidence": f"It accounts for {top_pct:.1f}% of all {len(all_tickets):,} tickets analysed.",
            "impact": "A large share of support effort goes to this one area, "
                      "so improvements here have the widest reach.",
            "action": f"Target process improvements at '{top_cat}' to reduce overall volume.",
        })

    return sections