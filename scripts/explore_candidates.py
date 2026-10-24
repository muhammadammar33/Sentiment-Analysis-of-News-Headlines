# Exploration used to find candidate headlines for the 10-headline close reading.
# Prints random examples containing common sentiment words, with their VADER scores.
# Run from the repository root: python scripts/explore_candidates.py
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
df = pd.read_json("data/Sarcasm_Headlines_Dataset_v2.json", lines=True)
df["headline"] = df["headline"].str.strip()
df = df.drop_duplicates("headline").reset_index(drop=True)
df["compound"] = df["headline"].apply(lambda h: analyzer.polarity_scores(h)["compound"])
df["label"] = pd.cut(df["compound"], [-1.01, -0.05, 0.0499999, 1.01], labels=["negative", "neutral", "positive"])

pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 120)
KEYWORDS = ["great", "love", "best", "happy", "dies", "killed", "not ", "win",
            "perfect", "thank", "wonderful", "fun", "proud", "hope"]
for kw in KEYWORDS:
    sample = df[df["headline"].str.contains(r"\b" + kw)].sample(6, random_state=1)
    print(f"== {kw}")
    print(sample[["is_sarcastic", "headline", "compound", "label"]].to_string(), "\n")

# Which everyday news words are (not) in VADER's lexicon?
for w in ["dies", "died", "killed", "fake", "hope", "fun", "perfectly", "prevent", "lays", "wonderful", "shooting"]:
    print(f"{w!r:12} in lexicon: {w in analyzer.lexicon}  value: {analyzer.lexicon.get(w)}")
