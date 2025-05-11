### Description
This repository contains structured solutions and analyses for a set of Natural Language Processing (NLP) tasks designed to cover key text mining and modeling concepts using Python or R.

### Exercise Sheet Summaries
### **1. Magic Card Data Structuring**
 - Extract and parse unstructured text descriptions of Magic: The Gathering cards.
 - Convert to a structured format with name, cost, type, and effect.
 - Analyze card types for frequency.

###  2. Movie Review Preprocessing & Text Normalization
 - Load and preprocess UTF-encoded movie reviews.
 - Apply tokenization, stemming, and lemmatization.
 - Perform frequency and stop word analysis.

###  3. Harry Potter Corpus Cleaning & TF-IDF
 - Preprocess full book texts to remove noise and structure by chapters.
 - Compute TF-IDF scores and analyze high-impact terms across books.

###  4. Sentiment Over Time in Song Lyrics
 - Load lyrics and preprocess for dictionary-based sentiment analysis.
 - Visualize average sentiment trends by year.

###  5. News Clustering: K-Means vs LDA
 - Use topic modeling and TF-IDF-based k-means clustering.
 - Compare clustering quality with known news categories.

###  6. A Song of Ice and Fire: Topic Evolution
 - Clean and segment books into chapters.
 - Train LDA models to explore theme progression across the series.


###  7. Emotion Classification via Seeded LDA
 - Train standard and seeded LDAs on tweets.
 - Compare topic modeling outcomes with emotion labels using confusion matrices.

###  8. U Biden Twitter Rolling LDA
 - Apply Rolling LDA on pre-election tweets.
 - Track topic shifts over time and compare with standard LDA.


###  9. Star Trek Word2Vec Similarity
 - Train Word2Vec models with different window sizes.
 - Measure inter-character and intra-show semantic similarity.

###  10. Fake News Classification with Embeddings
 - Use Doc2Vec and Word2Vec for document representation.
 - Train logistic regression classifiers to detect fake news.

### 11. Language Detection using HuggingFace
 - Use pre-trained transformer models to detect language in an unsupervised setting.

###  12. TREC Question Classification
 - Compare Doc2Vec, fine-tuned BERT, and BERT with LoRA adapters.
 - Evaluate with macro F1 scores for coarse and fine-grained labels.

###  13. Movie Genre Detection (Open Task)
 - Use unsupervised models (LDA, Word2Vec) to infer genres from movie summaries.

###  14. Bitcoin Subreddit Sentiment vs Price
 - Combine the post title and text for sentiment scoring.
 - Correlate daily sentiment with Bitcoin price fluctuations.

###  15. EU Parliament Protocol Parsing
 - Extract metadata and structure protocol documents using regex.
 - Automate text segmentation and cleanup.

###  16. arXiv Paper Classification
 - Build a pipeline for scientific paper classification using Doc2Vec, LDA, or BERT.

###  17. Trump Speech Preprocessing & Analysis
 - Clean and tokenize campaign speeches.
 - Apply stemming and lemmatization, and stop word removal.
