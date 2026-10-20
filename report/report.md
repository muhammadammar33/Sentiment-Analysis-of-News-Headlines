# Sentiment Analysis of News Headlines Using Python: Do Computational Labels Match Meaning?

## 1. Introduction

Sentiment analysis tries to work out automatically whether a piece of text expresses a positive, negative or neutral attitude. News headlines look like a simple case, because they are short and written in standard English. In practice they are hard. Headline writers compress a whole story into a few words, depend on the reader's background knowledge, and often use irony to get attention. This study applies VADER, a widely used lexicon-based sentiment tool, to more than 28,000 headlines. The question is not only *what* labels VADER produces, but **whether those labels match what the headlines actually mean.**

## 2. Data and Method

**Dataset.** I used the publicly available *News Headlines Dataset for Sarcasm Detection* (Misra & Arora, 2023). It contains 28,619 headlines: real news from *HuffPost* and satire from *The Onion*. Each headline has an `is_sarcastic` flag. I chose this dataset deliberately. It meets the requirement for a public headline corpus, and the satire label gives an independent way to test one of the best-known weaknesses of sentiment tools.

**Cleaning.** I loaded the data with pandas from its JSON-lines file. There were no missing or empty headlines. There were, however, 116 repeated headlines. The most frequent was the Onion headline *"'no way to prevent this,' says only nation where this regularly happens"*, which appears 12 times because The Onion republishes it after each mass shooting in the United States. I kept only the first occurrence of each headline, leaving **28,503 unique headlines** (14,951 real, 13,552 satirical). The average headline is about ten words long, and the whole dataset is in lower case.

**Tool.** VADER (Hutto & Gilbert, 2014) uses a dictionary of about 7,500 words. Each word has a human-rated score from −4 (very negative) to +4 (very positive). VADER adjusts those scores with rules for negation, intensifiers, "but"-clauses, punctuation and capitals, and combines everything into a *compound* score between −1 and +1.

**Decision rules.** I used the thresholds recommended by VADER's authors: compound ≥ 0.05 → *positive*; compound ≤ −0.05 → *negative*; anything in between → *neutral*.

## 3. Results

| Label | Count | Percentage |
|---|---:|---:|
| Negative | 9,402 | 33.0 % |
| Neutral | 10,200 | 35.8 % |
| Positive | 8,901 | 31.2 % |
| **Total** | **28,503** | **100 %** |

Taken at face value (Figures 1 and 2), the corpus looks evenly balanced: about a third of the headlines are negative, a third neutral and a third positive. Neutral is the largest group. Someone who only reported this output might conclude that news headlines are emotionally balanced. The rest of this section argues that this conclusion would be misleading.

**Finding 1: VADER cannot see satire.** If VADER detected the mocking or critical tone of satire, Onion headlines would score differently from real news. They do not (Figure 3). Real news is 32.0 % negative, 36.9 % neutral and 31.1 % positive. Satire is 34.1 % negative, 34.5 % neutral and 31.4 % positive. The mean compound scores are almost the same (−0.011 and −0.016). A chi-square test is formally significant, but only because the sample is very large: the effect size (Cramér's V ≈ 0.03) is negligible. Headlines written to mean the opposite of what they literally say get the same mix of labels as straightforward reporting.

**Finding 2: "Neutral" often means "unknown".** Figure 4 shows a sharp spike at a compound score of exactly 0. Of the 10,200 neutral headlines, **9,755 (95.6 %) contain no word from VADER's dictionary at all.** That is not the same as being neutral. Several basic news words are missing: the dictionary includes *died* but not ***dies***, and it lacks *shooting*, *hurricane*, *flood*, *layoffs* and *deported*. Death notices such as *"british singer and tv host cilla black dies at 72"* and *"8-year-old girl dies after drinking boiling water on dare"* therefore get a score of 0.0. Part of the large neutral category is a gap in the dictionary, not a property of the news.

**Finding 3: The categories depend on the researcher's thresholds.** If the neutral band is widened from ±0.05 to ±0.20, the neutral share grows from 35.8 % to 43.3 %. At ±0.50 it reaches 74.7 %. Any statement like "a third of headlines are negative" depends on a modelling choice as much as on the language.

## 4. Critical Examination of Ten Headlines

I selected ten headlines to cover different kinds of language. For each one, I compared VADER's label with my own reading and recorded the dictionary words that drove the score.

| # | Headline (abridged) | VADER | Human | Words that drove the score |
|---|---|---|---|---|
| 1 | student killed herself after university mishandled her rape report | neg (−0.88) | neg | killed, rape |
| 2 | mexico mayor killed less than a day after taking office | neg (−0.67) | neg | killed |
| 3 | british singer and tv host cilla black dies at 72 | neutral (0.00) | neg | none |
| 4 | how fake meat may change our future thanksgiving dinners | neg (−0.48) | neutral | fake |
| 5 | duke students refuse to read 'fun home' over gay themes, nudity | pos (+0.27) | neg | refuse, fun |
| 6 | bob hope happy to see so many troops in heaven | pos (+0.87) | neg | hope, happy, heaven |
| 7 | …underfunded public schools… leave students perfectly prepared for rest of life | pos (+0.82) | neg | support, perfectly, prepared |
| 8 | 'no way to prevent this,' says only nation where this regularly happens | neutral (+0.03) | neg | no, prevent |
| 9 | boeing lays off only guy who knows how to keep wings on plane | neutral (0.00) | neg | none |
| 10 | why i'm thinking of separating from a wonderful man after 27 years together | pos (+0.57) | neg / mixed | wonderful |

VADER matched my reading in only **2 of the 10** cases. Because I chose these examples to probe weaknesses, this is not an accuracy estimate. Its value is in showing *how* the method fails.

*Where VADER works (1–2).* Both headlines report tragedies with a single strong emotional word ("killed"). Here the surface wording and the meaning agree, so word-counting gives the right answer.

*Missing vocabulary (3, 9).* Headline 3 is a death notice that scores zero because the dictionary contains "died" but not "dies". In headline 9, "lays off" is also absent. The headline is alarming, but VADER sees no sentiment words.

*Word sense and named entities (4–6).* In headline 4, "fake meat" means plant-based meat, not deception, so VADER's −2.1 for "fake" turns a neutral food article negative. In headline 5, *Fun Home* is the title of a graphic memoir, and its "fun" outweighs the real topic, which is a refusal to read a book over its content. In headline 6, "Hope" is the comedian Bob Hope's surname, but VADER scores it as the emotion hope.

*Sarcasm and irony (6–8).* These are Onion headlines. Headline 7 gets a strongly positive score (+0.82) because "support", "perfectly" and "prepared" are positive words, yet the intended meaning is bitter criticism of underfunded schools. Headline 6 jokes about soldiers' deaths with cheerful words. Headline 8 gets a slightly positive score because VADER reads "no" as negating "prevent", while the headline is one of the darkest pieces of political satire in the dataset.

*Implied meaning (8–9).* The negativity in these headlines comes from the situation (a plane without wings, a nation that does nothing), so understanding it requires world knowledge that a dictionary does not have.

*Mixed meaning (10).* "Wonderful" describes the husband, but the headline is about ending a 27-year marriage. A single number cannot capture both, and different readers might also disagree here. This shows that even "human" sentiment labels are not always clear-cut.

## 5. Limitations of Automated Sentiment Analysis

1. **Sarcasm and irony.** Lexicon methods take words at face value. The near-identical profiles of satire and real news (Cramér's V ≈ 0.03) show this clearly.
2. **Ambiguity.** Word sense (fake meat versus fake news) and proper nouns (Hope, *Fun Home*) are not handled.
3. **Context and world knowledge.** Headlines are short and assume a lot of background knowledge. The meaning often lies in a situation rather than in emotional words.
4. **Dictionary coverage.** Missing words push headlines into "neutral" and hide negative news events.
5. **Unclear target.** VADER does not separate the *topic* (a tragedy), the *writer's stance* (neutral reporting) and the *reader's likely reaction*. A neutrally worded report of a death is "negative news" but not necessarily "negative sentiment".
6. **Arbitrary thresholds and preprocessing.** The category sizes change a lot with the cut-off, and because the dataset is all lower case, VADER's capitalisation rule never applies.
7. **Limits of this study.** The dataset labels sarcasm, not sentiment, so I could show VADER's blind spots but could not measure its overall accuracy. Next steps would be to have several people annotate a random sample (and measure their agreement) and to compare VADER with a context-aware transformer model.

## 6. Conclusion

VADER is quick, transparent and easy to interpret, and it works well when a headline states its emotion directly. However, its apparently balanced output (33 % negative, 36 % neutral, 31 % positive) hides three serious problems: it cannot tell satire from sincere reporting, most of its "neutral" labels come from missing vocabulary, and its category sizes depend on arbitrary thresholds. Computational sentiment labels should therefore be treated as a first rough pass that needs to be checked by reading the headlines, not as a direct measure of what headlines mean.

## References

- Hutto, C. J., & Gilbert, E. (2014). VADER: A parsimonious rule-based model for sentiment analysis of social media text. *Proceedings of the International AAAI Conference on Web and Social Media, 8*(1), 216–225.
- Misra, R., & Arora, P. (2023). Sarcasm detection using news headlines dataset. *AI Open, 4*, 13–18.
- Misra, R., & Grover, J. (2021). *Sculpting Data for ML: The first act of Machine Learning.* ISBN 9798585463570.
- Dataset: https://github.com/rishabhmisra/News-Headlines-Dataset-For-Sarcasm-Detection
