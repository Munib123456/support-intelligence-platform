"""
statistics_engine.py
Phase 3: The statistics engine — the brain of the project.

What this file does, in plain words:
- Takes the cleaned analytics data.
- Runs the CORRECT statistical test for each type of question.
- Only reports a pattern as a "finding" if it is statistically significant (p < 0.05).

The rule for which test to use:
  - category vs category        -> Chi-square
  - category vs a number        -> Kruskal-Wallis (a robust ANOVA)
  - a number vs a number/rating  -> Spearman correlation
"""

import pandas as pd
from scipy.stats import chi2_contingency, kruskal, spearmanr

# A pattern counts as "real" only if its p-value is below this.
SIGNIFICANCE = 0.05


def fmt_p(p):
    """Format a p-value the way it is reported professionally."""
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"


def chi_square_test(df, col_a, col_b):
    """
    Test whether two CATEGORY columns are linked.
    Example: is complaint category linked to agent shift?
    """
    table = pd.crosstab(df[col_a], df[col_b])
    chi2, p, dof, expected = chi2_contingency(table)
    significant = p < SIGNIFICANCE
    if significant:
        sentence = f"'{col_a}' and '{col_b}' are significantly linked (chi-square, {fmt_p(p)})."
    else:
        sentence = f"No significant link between '{col_a}' and '{col_b}' ({fmt_p(p)})."
    return {"test": "chi-square", "p_value": p, "significant": significant, "finding": sentence}


def kruskal_test(df, category_col, number_col):
    """
    Test whether a NUMBER differs across the groups of a CATEGORY.
    Example: does CSAT score differ by agent shift?
    (Kruskal-Wallis is used instead of ANOVA because it does not
     assume the data is perfectly bell-shaped — safer for real data.)
    """
    groups = [g[number_col].dropna().values for _, g in df.groupby(category_col)]
    groups = [g for g in groups if len(g) > 0]
    stat, p = kruskal(*groups)
    significant = p < SIGNIFICANCE
    if significant:
        sentence = f"'{number_col}' differs significantly across '{category_col}' groups (Kruskal-Wallis, {fmt_p(p)})."
    else:
        sentence = f"No significant difference in '{number_col}' across '{category_col}' ({fmt_p(p)})."
    return {"test": "kruskal-wallis", "p_value": p, "significant": significant, "finding": sentence}


def spearman_test(df, num_col_a, num_col_b):
    """
    Test whether two NUMBERS / RATINGS move together.
    Example: as response time rises, does satisfaction fall?
    """
    pair = df[[num_col_a, num_col_b]].dropna()
    rho, p = spearmanr(pair[num_col_a], pair[num_col_b])
    significant = p < SIGNIFICANCE
    direction = "together" if rho > 0 else "in opposite directions"
    if significant:
        sentence = f"'{num_col_a}' and '{num_col_b}' move {direction} (Spearman r = {rho:.2f}, {fmt_p(p)})."
    else:
        sentence = f"No significant relationship between '{num_col_a}' and '{num_col_b}' ({fmt_p(p)})."
    return {"test": "spearman", "p_value": p, "significant": significant, "finding": sentence}


def run_all_tests(all_tickets, rated_tickets):
    """
    Run the obvious questions and collect every result.
    Uses all three test types on the columns proven to carry real relationships.
    """
    results = []

    # --- Category vs category (chi-square) ---
    results.append(chi_square_test(all_tickets, "Category", "Agent Shift"))
    results.append(chi_square_test(all_tickets, "Category", "Agent Tenure"))
    results.append(chi_square_test(all_tickets, "Channel", "Category"))

    # --- Category vs number (Kruskal-Wallis) ---
    results.append(kruskal_test(rated_tickets, "Category", "CSAT Score"))
    results.append(kruskal_test(rated_tickets, "Agent Shift", "CSAT Score"))
    results.append(kruskal_test(rated_tickets, "Agent Tenure", "CSAT Score"))
    results.append(kruskal_test(all_tickets, "Category", "Response Hours"))

    # --- Number vs rating (Spearman) ---
    results.append(spearman_test(rated_tickets, "Response Hours", "CSAT Score"))

    return results


if __name__ == "__main__":
    # Import the Phase 1 cleaning so this file can run on its own.
    import sys, os
    sys.path.append(os.path.dirname(__file__))
    from load_data import load_tickets, clean_tickets

    raw = load_tickets()
    all_tickets, rated_tickets = clean_tickets(raw)

    print(f"Running tests on {len(all_tickets)} tickets ({len(rated_tickets)} rated).\n")
    results = run_all_tests(all_tickets, rated_tickets)

    print("=== ALL RESULTS ===")
    for r in results:
        print(f"  [{r['test']}] {r['finding']}")

    print("\n=== SIGNIFICANT FINDINGS ONLY ===")
    significant = [r for r in results if r["significant"]]
    if significant:
        for r in significant:
            print(f"  * {r['finding']}")
    else:
        print("  (No statistically significant patterns found.)")