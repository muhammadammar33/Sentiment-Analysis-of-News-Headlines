# Step-by-Step Guide: How This Project Was Built

This guide records every step used to produce the project: where the data came from, how the environment was set up, how the analysis pipeline works, how the 10 example headlines were chosen, and how the notebook, report, presentation and GitHub repository were created. Following it from top to bottom reproduces every file in the repository.

## Contents

1. Project structure
2. Tools and environment setup
3. Finding and downloading the dataset
4. Loading the data with pandas
5. Inspecting and cleaning the data
6. Applying VADER
7. Classifying headlines with decision rules
8. Counting headlines per category
9. Making the charts
10. Going beyond the output: three extra analyses
11. Choosing and examining the 10 headlines
12. Writing up the limitations
13. Building and running the notebook
14. Writing the research report
15. Building the presentation
16. Checking the documents visually
17. Putting the project on GitHub
18. Reproducing everything with one set of commands
19. Key numbers for the presentation

## 1. Project structure

| Path | What it is |
|---|---|
| `data/Sarcasm_Headlines_Dataset_v2.json` | The dataset (28,619 headlines) |
| `data/SOURCE.md` | Where the dataset came from and how to cite it |
| `sentiment_analysis_news_headlines.ipynb` | The main Python notebook, with outputs saved |
| `outputs/tables/*.csv` | Tables produced by the notebook |
| `outputs/figures/*.png` | Charts produced by the notebook |
| `report/report.md`, `report/report.docx` | The research report |
| `presentation/presentation.pptx` | The 10-slide presentation |
| `scripts/build_notebook.py` | Writes the notebook cell by cell |
| `scripts/explore_candidates.py` | Exploration used to find example headlines |
| `scripts/build_report_and_slides.py` | Turns the report text into Word and builds the slides |
| `scripts/build_guide_docx.py` | Turns this guide into a Word file |
| `requirements.txt` | Python packages needed |
| `docs/step_by_step_guide.md`, `.docx` | This guide |

## 2. Tools and environment setup

**What was used**

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.13 | Programming language |
| pandas | 3.0.5 | Loading and handling the data table |
| numpy | (installed with pandas) | Numeric helpers |
| vaderSentiment | 3.3.2 | The sentiment analysis tool |
| matplotlib | 3.11.2 | Charts |
| scipy | 1.18.1 | Chi-square test |
| jupyter, nbformat, nbconvert | 5.11 / 7.17 | Creating and running the notebook |
| python-docx | 1.2.0 | Creating the Word report |
| python-pptx | 1.0.2 | Creating the PowerPoint slides |
| LibreOffice | 24.2 | Converting the Word and PowerPoint files to PDF to check them visually (optional) |
| Git | any | Version control and uploading to GitHub |

**How to install**

Open a terminal in the project folder and run:

```
pip install pandas numpy matplotlib scipy vaderSentiment jupyter nbformat nbconvert python-docx python-pptx
```

or, for just the notebook's packages:

```
pip install -r requirements.txt
```

*Why VADER?* The assignment suggests VADER. It also suits this project well: it needs no training data, it is designed for short texts, and it is transparent. You can look up exactly which words gave a headline its score, which makes it possible to explain *why* a label is wrong.

## 3. Finding and downloading the dataset

**Requirement:** a public dataset with at least 200 news headlines.

**Choice:** the *News Headlines Dataset for Sarcasm Detection* by Rishabh Misra.

- GitHub page: https://github.com/rishabhmisra/News-Headlines-Dataset-For-Sarcasm-Detection
- Also on Kaggle: https://www.kaggle.com/datasets/rmisra/news-headlines-dataset-for-sarcasm-detection
- Contents: 28,619 headlines. Real news from *HuffPost* (`is_sarcastic = 0`) and satirical news from *The Onion* (`is_sarcastic = 1`).

**Why this dataset and not another?** It meets the requirement (public, more than 200 headlines), and it has one extra feature: every headline is already tagged as satire or real news. The assignment asks you to discuss sarcasm as a limitation (Task 9). With this label, that discussion can be backed by numbers (does VADER score satire differently from real news?) instead of only a few examples.

**How it was downloaded.** The raw file was downloaded from the GitHub repository with `curl`:

```
curl -L -o Sarcasm_Headlines_Dataset_v2.json "https://raw.githubusercontent.com/rishabhmisra/News-Headlines-Dataset-For-Sarcasm-Detection/master/Sarcasm_Headlines_Dataset.json"
```

The downloaded file has 28,619 records, which matches the figure the dataset's README gives for version 2 of the dataset. It was saved in the project as `data/Sarcasm_Headlines_Dataset_v2.json`. If you prefer a browser, you can download the same data from the Kaggle page (free account needed).

**Checking the file before using it.** The first lines were printed to confirm the format:

```
head -c 600 data/Sarcasm_Headlines_Dataset_v2.json
```

Each line is one JSON record with three fields, for example:

```
{"is_sarcastic": 1, "headline": "thirtysomething scientists unveil doomsday clock of hair loss", "article_link": "https://www.theonion.com/..."}
```

The source and citation were written into `data/SOURCE.md`, because the assignment asks for "the dataset and its source".

## 4. Loading the data with pandas (Task 2)

The file is in *JSON Lines* format (one JSON object per line), so pandas reads it with `lines=True`:

```
import pandas as pd
raw = pd.read_json("data/Sarcasm_Headlines_Dataset_v2.json", lines=True)
print(raw.shape)      # (28619, 3)
raw.head()
```

## 5. Inspecting and cleaning the data (Task 3)

**5.1 Inspect.** `raw.info()` shows the column types and that no column has missing values.

**5.2 Check for problems.** Six checks were run and collected in one table:

```
checks = pd.Series({
    "missing headline (NaN)": raw["headline"].isna().sum(),
    "empty / whitespace-only headline": (raw["headline"].astype(str).str.strip() == "").sum(),
    "missing is_sarcastic": raw["is_sarcastic"].isna().sum(),
    "fully duplicated rows": raw.duplicated().sum(),
    "duplicated article_link": raw["article_link"].duplicated().sum(),
    "duplicated headline text": raw["headline"].str.strip().duplicated().sum(),
})
```

Results: **0 missing values, 0 empty headlines, 2 fully duplicated rows and 116 repeated headline texts.**

**5.3 Look at the duplicates before deleting them.** Grouping by headline showed the most repeated ones. The top one, *"'no way to prevent this,' says only nation where this regularly happens"* (12 times), is an Onion headline that is republished after every mass shooting in the United States. Others are repeated HuffPost column titles such as "sunday roundup".

**5.4 Clean.** Decision: keep one copy of each headline, because repeats would give extra weight to a few texts.

```
df = raw.copy()
df["headline"] = df["headline"].str.strip()                 # remove stray spaces
df = df.dropna(subset=["headline"])                         # drop missing (none here, but safe)
df = df[df["headline"] != ""]                               # drop empty (none here)
df = df.drop_duplicates(subset="headline", keep="first").reset_index(drop=True)
df["source"] = df["is_sarcastic"].map({0: "HuffPost (real)", 1: "The Onion (satire)"})
```

Result: **28,503 unique headlines** (14,951 HuffPost and 13,552 Onion).

**5.5 Notice the text format.** Headline length was measured (`df["headline"].str.split().str.len()`, about 10 words on average). Reading the rows also showed that **every headline is in lower case**. This matters later, because VADER normally uses CAPITALS as a sign of strong emotion.

## 6. Applying VADER (Task 4)

**How VADER works (in short).** VADER has a dictionary of about 7,500 words. People rated each word from −4 (very negative) to +4 (very positive). VADER adds up the scores of the words it finds, with rules for negation ("not good"), intensifiers ("very"), "but", exclamation marks and capitals. The result is four numbers:

- `neg`, `neu`, `pos`: the proportions of negative, neutral and positive content
- `compound`: one overall score from −1 (most negative) to +1 (most positive)

**Code:**

```
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()
scores = df["headline"].apply(analyzer.polarity_scores).apply(pd.Series)
df = pd.concat([df, scores], axis=1)
```

Each headline now has `neg`, `neu`, `pos` and `compound` columns.

## 7. Classifying headlines with decision rules (Task 5)

The thresholds recommended by VADER's authors (Hutto & Gilbert, 2014) were used and written down in the notebook:

| Rule | Condition | Label |
|---|---|---|
| R1 | compound ≥ +0.05 | positive |
| R2 | compound ≤ −0.05 | negative |
| R3 | anything in between | neutral |

```
POS_T, NEG_T = 0.05, -0.05
def classify(compound, pos_t=POS_T, neg_t=NEG_T):
    if compound >= pos_t:
        return "positive"
    if compound <= neg_t:
        return "negative"
    return "neutral"

df["label"] = df["compound"].apply(classify)
```

The thresholds are parameters of the function, so the same function can be reused later to test other thresholds (Step 10.3).

## 8. Counting headlines per category (Task 6)

```
summary = df["label"].value_counts().reindex(["negative", "neutral", "positive"]).rename("count").to_frame()
summary["percentage"] = (summary["count"] / summary["count"].sum() * 100).round(2)
summary.to_csv("outputs/tables/sentiment_distribution.csv")
```

| Label | Count | % |
|---|---:|---:|
| negative | 9,402 | 32.99 |
| neutral | 10,200 | 35.79 |
| positive | 8,901 | 31.23 |
| total | 28,503 | 100 |

The same counts were also split by source with `pd.crosstab(df["source"], df["label"])` and saved to `outputs/tables/sentiment_by_source.csv`.

## 9. Making the charts (Task 7)

**Colour choice.** Sentiment runs from negative to positive, so the charts use two opposite colours with grey in the middle: red (#e34948) for negative, grey (#a3a29c) for neutral and blue (#2a78d6) for positive. The same colours are used in every chart so the reader learns them once. Every bar also shows its number and percentage, so the charts can be read without relying on colour alone.

Four charts were made with matplotlib and saved at 200 dpi in `outputs/figures/`:

| File | Chart | Why |
|---|---|---|
| `fig1_sentiment_bar.png` | Bar chart of the three labels, with count and % above each bar | Required chart (Task 7) |
| `fig2_sentiment_pie.png` | Pie chart of the same shares | Required chart (Task 7, alternative form) |
| `fig3_sentiment_by_source.png` | 100% stacked bars: Onion vs. HuffPost | Shows that satire gets the same labels as real news |
| `fig4_compound_distribution.png` | Histogram of compound scores for each source, neutral band shaded | Shows the large spike at exactly 0 |

Each chart follows the same pattern: create the figure, draw, add labels and a title that states the finding, then save:

```
fig, ax = plt.subplots(figsize=(7, 4.2))
bars = ax.bar(ORDER, counts, color=[COLOURS[k] for k in ORDER])
...
plt.savefig("outputs/figures/fig1_sentiment_bar.png", dpi=200, bbox_inches="tight")
```

## 10. Going beyond the output: three extra analyses

The assignment says not to just report the model's output. Three analyses were added to test whether the labels can be trusted.

**10.1 Does VADER notice sarcasm?** If it did, Onion headlines would get more negative or at least different scores.

- Compared the label percentages and mean `compound` score for each source.
- Ran a chi-square test of independence on the source × label table (`scipy.stats.chi2_contingency`).
- Calculated **Cramér's V**, an effect size between 0 and 1: V = √(χ² / (n × (k − 1))), where k is the smaller number of rows or columns.

Result: χ² = 21.9, p < 0.001, **but V ≈ 0.03 (negligible)**. With 28,000 headlines even tiny differences come out "significant", which is why the effect size is reported. Conclusion: VADER treats satire almost exactly like real news.

**10.2 Are neutral headlines really neutral?** For each headline, the words found in VADER's dictionary (`analyzer.lexicon`) were listed:

```
lex = analyzer.lexicon
def lexicon_hits(text):
    toks = [t.strip(".,!?:;'\"()[]") for t in text.split()]
    return [t for t in toks if t in lex]
```

Result: **9,755 of the 10,200 neutral headlines (95.6 %) contain no dictionary word at all.** Common news words were then checked one by one: "died" is in the dictionary but **"dies" is not**, and neither are "shooting", "hurricane", "flood", "layoffs" or "deported". A search for neutral headlines containing those words found 95 examples, including death notices scored 0.0.

**10.3 Do the thresholds change the result?** The `classify` function was re-run with neutral bands of ±0.05, ±0.10, ±0.20, ±0.30 and ±0.50. The neutral share grows from 35.8 % to 43.3 % (±0.20) and 74.7 % (±0.50). The table is saved as `outputs/tables/threshold_sensitivity.csv`.

## 11. Choosing and examining the 10 headlines (Task 8)

**11.1 Finding candidates.** `scripts/explore_candidates.py` was run. For common sentiment words (great, love, best, happy, dies, killed, not, win, perfect, thank, wonderful, fun, proud, hope) it prints six random headlines containing the word, with their VADER score, label and source. It also checks which words are in VADER's dictionary.

```
python scripts/explore_candidates.py
```

**11.2 Reading and selecting.** The printed candidates were read one by one. Ten were chosen so that each type of situation appears at least once:

| Type of case | Headlines chosen |
|---|---|
| VADER is right (explicit emotional word) | #1 student killed herself…, #2 mexico mayor killed… |
| Word missing from the dictionary | #3 cilla black dies at 72, #9 boeing lays off… |
| Word sense (a word with a different meaning) | #4 fake meat… |
| Named entity (a name or title read as an emotion) | #5 'fun home', #6 bob hope… |
| Sarcasm / irony (Onion) | #6, #7 schools "perfectly prepared", #8 'no way to prevent this' |
| Implied meaning (needs world knowledge) | #8, #9 |
| Mixed / debatable meaning | #10 separating from a wonderful man |

Two correct cases were included on purpose, so the analysis shows where VADER works as well as where it fails.

**11.3 Recording a human reading.** For each headline, a human judgement (negative, neutral, positive or mixed) was written down by reading the headline and thinking about what it means in context. A short reason was added for each.

**11.4 Showing which words drove the score.** A helper function lists each dictionary word in the headline with its value. This explains each error. For example, headline #7 gets +0.82 because "support" (+1.7), "perfectly" (+3.2) and "prepared" (+0.9) are positive, even though the meaning is negative.

```
def drivers(text):
    toks = [t.strip(".,!?:;'\"()[]") for t in text.split()]
    return ", ".join(f"{t} ({lex[t]:+.1f})" for t in toks if t in lex) or "— none —"
```

**11.5 Result.** VADER agreed with the human reading in 2 of 10 cases. Because the headlines were chosen to probe weak spots, this is reported as an illustration of *how* errors happen, not as an accuracy rate. The table is saved as `outputs/tables/close_reading_10_headlines.csv`.

## 12. Writing up the limitations (Task 9)

The limitations section was built from the evidence above, not from general statements:

| Limitation | Evidence used |
|---|---|
| Sarcasm and irony | Cramér's V ≈ 0.03 (Step 10.1); headlines #6–8 |
| Ambiguity | "fake meat", "Bob Hope", "Fun Home" (#4–6) |
| Context and world knowledge | #8, #9 |
| Dictionary coverage | 95.6 % of neutrals have no dictionary word; "dies" missing (Step 10.2) |
| Topic vs. stance vs. reader reaction | Death notices written in neutral language |
| Thresholds and preprocessing | Step 10.3; all-lower-case text disables the capitals rule |
| Limits of this study | The dataset labels sarcasm, not sentiment, so overall accuracy cannot be measured |

## 13. Building and running the notebook (deliverable 1)

**13.1 Generate the notebook.** `scripts/build_notebook.py` uses the `nbformat` library to write `sentiment_analysis_news_headlines.ipynb`. It adds markdown cells (explanations) and code cells (the code from Steps 4–12) in order. Writing the notebook from a script makes it easy to change text and rebuild it in one go. You could also type the same cells into Jupyter by hand.

```
python scripts/build_notebook.py
```

**13.2 Run every cell and save the outputs.** The notebook is executed from top to bottom, and the results (tables, printed text, charts) are saved inside it, so the marker can see them without running anything:

```
jupyter nbconvert --to notebook --execute --inplace sentiment_analysis_news_headlines.ipynb
```

Running the notebook also writes every file in `outputs/tables/` and `outputs/figures/`.

**13.3 Check and fix.** The outputs were read after each run, and these problems were fixed:

- `scipy` was not installed at first, so it was installed with `pip install scipy`.
- Counts showed as "9,402.0" because adding the total row turned them into decimals. Fixed with `.astype(int)`.
- The keyword "shot" matched phrases like "a shot in the arm", so it was removed from the search for negative news words.
- The text said "cancer" was missing from the dictionary, but it is not missing. The text was corrected to list only words that really are missing.

**13.4 Open it yourself.** `jupyter notebook sentiment_analysis_news_headlines.ipynb`, then Kernel → Restart & Run All.

## 14. Writing the research report (deliverable 4)

**14.1 Structure.** The report follows the order of the research: Introduction → Data and Method → Results (three findings) → Critical examination of ten headlines → Limitations → Conclusion → References.

**14.2 Writing.** The text was written in Markdown (`report/report.md`). Every number in it was copied from the notebook output, so the report and the notebook agree.

**14.3 Word count check.** The assignment asks for about 1,000–1,500 words. The prose was counted without tables and references:

```
python -c "import re;t=open('report/report.md').read().split('## References')[0];t='\n'.join(l for l in t.splitlines() if not l.startswith('|'));print(len(re.findall(r\"[A-Za-z0-9']+\",t)))"
```

Result: about 1,370 words.

**14.4 Convert to Word.** `scripts/build_report_and_slides.py` reads `report.md` line by line with `python-docx`. It turns `#`/`##` lines into headings, `|` lines into tables, numbered and `-` lines into lists, and `**bold**`/`*italic*` into formatting. It inserts Figures 1–4 with captions in the Results section and sets the author name in the file properties. Output: `report/report.docx`.

## 15. Building the presentation (deliverable 5)

The same script builds `presentation/presentation.pptx` with `python-pptx`: 10 widescreen slides (13.33 × 7.5 inches).

1. Title
2. Research question and data
3. Method: VADER and decision rules
4. Results (bar chart and numbers)
5. Finding 1: VADER cannot see satire (stacked bar chart)
6. Finding 2: "Neutral" often means "unknown" (histogram) and Finding 3 (thresholds)
7. Close reading: table of the 10 headlines, with VADER labels coloured red/blue
8. Why VADER goes wrong
9. Conclusion
10. References

```
python scripts/build_report_and_slides.py
```

## 16. Checking the documents visually

Files built by code can look different from what you expect, so both were converted to PDF with LibreOffice and turned into images to check:

```
soffice --headless --convert-to pdf presentation/presentation.pptx report/report.docx
pdftoppm -r 40 -png presentation.pdf slide
```

Problems found and fixed:

- On slide 5, the text overlapped the chart's axis label. The chart was made smaller and the text moved down.
- In the Word report, the headline column of the 10-headline table was too narrow. Fixed column widths were set.

## 17. Putting the project on GitHub

```
git config user.name "Muhammad Ammar"
git config user.email "muhammadammar7747@gmail.com"
git add -A
git commit -m "Add sentiment analysis of news headlines assignment"
git push origin <working-branch>:main
```

A `.gitignore` excludes `.ipynb_checkpoints/` and `__pycache__/`. The repository's default branch is `main`.

## 18. Reproducing everything with one set of commands

From the repository root:

```
pip install pandas numpy matplotlib scipy vaderSentiment jupyter nbformat nbconvert python-docx python-pptx
python scripts/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace sentiment_analysis_news_headlines.ipynb
python scripts/explore_candidates.py
python scripts/build_report_and_slides.py
```

This recreates the notebook (with outputs), all tables and charts, the Word report and the slides. The data file is already in `data/`, so no download is needed.

## 19. Key numbers for the presentation

| Item | Value |
|---|---|
| Headlines downloaded | 28,619 |
| Duplicates removed | 116 |
| Headlines analysed | 28,503 (14,951 HuffPost, 13,552 Onion) |
| Negative / neutral / positive | 9,402 (33.0 %) / 10,200 (35.8 %) / 8,901 (31.2 %) |
| Satire vs. real news | Cramér's V ≈ 0.03 (negligible difference) |
| Neutral headlines with no dictionary word | 9,755 (95.6 %) |
| Neutral share at ±0.20 / ±0.50 thresholds | 43.3 % / 74.7 % |
| Close reading agreement | 2 of 10 (chosen to probe weaknesses, not an accuracy rate) |

## References

- Hutto, C. J., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225.
- Misra, R., & Arora, P. (2023). Sarcasm detection using news headlines dataset. *AI Open, 4*, 13–18.
- Misra, R., & Grover, J. (2021). *Sculpting Data for ML: The first act of Machine Learning.* ISBN 9798585463570.
- VADER source code: https://github.com/cjhutto/vaderSentiment
