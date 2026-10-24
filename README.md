# Sentiment Analysis of News Headlines Using Python

NLP mini assignment (submission: 26 October 2026).

**Objective:** apply VADER sentiment analysis to news headlines and evaluate whether the computationally assigned labels match what the headlines actually mean.

## Deliverables

| Deliverable | File |
|---|---|
| Python notebook | [`sentiment_analysis_news_headlines.ipynb`](sentiment_analysis_news_headlines.ipynb) |
| Dataset and source | [`data/Sarcasm_Headlines_Dataset_v2.json`](data/), [`data/SOURCE.md`](data/SOURCE.md) |
| Tables | [`outputs/tables/`](outputs/tables/) (CSV) |
| Visualisations | [`outputs/figures/`](outputs/figures/) (PNG) |
| Research report (~1,370 words) | [`report/report.docx`](report/report.docx), [`report/report.md`](report/report.md) |
| Presentation (10 slides) | [`presentation/presentation.pptx`](presentation/presentation.pptx) |
| Step-by-step guide (how everything was built) | [`docs/step_by_step_guide.docx`](docs/step_by_step_guide.docx), [`docs/step_by_step_guide.md`](docs/step_by_step_guide.md) |
| Build scripts | [`scripts/`](scripts/) |

## Key findings

- Of 28,503 unique headlines: **33.0 % negative, 35.8 % neutral, 31.2 % positive** (VADER compound, ±0.05 thresholds).
- **VADER cannot see satire:** Onion and HuffPost headlines receive almost identical label distributions (Cramér's V ≈ 0.03).
- **"Neutral" often means "unknown":** 95.6 % of neutral headlines contain no word from VADER's dictionary. "dies", "shooting", "hurricane" and "layoffs" are missing from it.
- **Thresholds matter:** widening the neutral band to ±0.20 raises the neutral share to 43 %.
- In a close reading of 10 headlines, VADER matched the human reading in only 2. The failures come from sarcasm, word sense ("fake meat"), proper nouns ("Bob Hope", *Fun Home*), implied meaning and missing vocabulary.

## How to run

```bash
pip install -r requirements.txt
jupyter notebook sentiment_analysis_news_headlines.ipynb
```

Run all cells from the repository root. The notebook regenerates every table and figure in `outputs/`. To rebuild every file (notebook, report, slides), follow Step 18 of the step-by-step guide.
