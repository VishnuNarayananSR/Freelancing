import pandas as pd
from gensim.models import Word2Vec
import nltk
import seaborn as sns
import matplotlib.pyplot as plt

nltk.download('stopwords')


def semantic_distance(keywords_file, title, body):
    kw_df = pd.read_excel(keywords_file)
    stop_words = nltk.corpus.stopwords.words('english')
    tokens_vector = []
    for idx in title.index:
        if pd.isna(title[idx]) or pd.isna(body[idx]):
            continue
        content = title[idx] + '\n' + body[idx]
        filtered_tokens = []
        tokens = nltk.tokenize.word_tokenize(content)
        for token in tokens:
            if token.isalpha() and token not in stop_words:
                filtered_tokens.append(token)
        tokens_vector.append(filtered_tokens)
    model = Word2Vec(sentences=tokens_vector, vector_size=100,min_count=1,sg=1)
    kw_df = pd.read_excel('keywords.xlsx')
    kw_df.set_index('Keywords', inplace=True)
    for row in kw_df.index:
        for col in kw_df.columns:
            kw_df[row][col] = model.wv.n_similarity(row.split(), col.split())
    kw_df.to_excel('distance.xlsx')
    sns.heatmap(kw_df)
    plt.tight_layout()
    plt.show()

df = pd.read_csv("article_data.csv")
semantic_distance("keywords.xlsx", df['Title'], df['Body'])

