# Customer Support Intelligence Platform

A business decision-support tool that turns thousands of customer support records into clear findings, statistical evidence, and prioritised recommendations — automatically.

**Live app:** https://munib-support-intelligence.streamlit.app

---

## The problem

Large organisations receive thousands of support tickets a month. Managers cannot read them all, so recurring problems stay hidden, response times creep up, and customer satisfaction quietly falls. This platform acts as an automated support analyst: it categorises issues, finds statistically significant patterns, and produces evidence-based recommendations a decision-maker can act on.

## What it does

- **Categorises** support issues using a Natural Language Processing (NLP) text classifier.
- **Tests for real patterns** using the correct statistical test for each type of data.
- **Generates recommendations**, each one tied to a specific statistical finding.
- **Produces an Executive Brief** — a plain-language summary for decision-makers, structured as Finding → Evidence → Business Impact → Recommended Action.
- Works on the built-in sample data, or on any support CSV you upload.

## Key principle

Statistics decide the facts; the language model only phrases the summary. Every finding and every number comes from statistical analysis, never from the model. This keeps the output defensible and avoids "the AI made it up".

## Method

| Question type | Example | Test used |
|---|---|---|
| Category vs category | Complaint category vs agent shift | Chi-square |
| Category vs a number | CSAT score across categories | Kruskal-Wallis |
| Number vs number/rating | Response time vs satisfaction | Spearman correlation |

A result is only reported as a finding when p < 0.05. Because the dataset is large, effect size (e.g. the Spearman r) is also reported, to show how strong each relationship actually is — not just that it is statistically detectable.

## Example findings (built-in data, ~82,000 records)

- Response time and satisfaction are negatively correlated (Spearman r = -0.19, p < 0.001): longer waits are associated with lower satisfaction.
- Satisfaction differs significantly by complaint category, agent shift, and agent tenure (Kruskal-Wallis, p < 0.001).

## Data

- **Analytics dataset:** a public customer support dataset (~82,000 real records) with category, channel, response timestamps, agent attributes, and CSAT scores.
- **NLP training dataset:** the CFPB Consumer Complaint Database — real, human-written complaint narratives with verified category labels, used to train and evaluate the classifier (~87% accuracy on held-out data).

## Tech stack

Python · pandas · scikit-learn · SciPy · Streamlit · Plotly

## Project structure

```
.
├── app.py                     # Streamlit dashboard (the front end)
├── src/
│   ├── load_data.py           # load and clean the data
│   ├── classifier.py          # NLP text classifier
│   ├── statistics_engine.py   # statistical tests
│   ├── recommendations.py     # findings -> prioritised actions
│   └── executive_brief.py     # plain-language summary
├── data/                      # sample dataset
├── requirements.txt
└── .streamlit/config.toml     # theme
```

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown in the terminal.
