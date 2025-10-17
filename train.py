import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from surprise import SVD, Dataset, Reader

# ===== 1. Load dataset =====
movies = pd.read_csv("movies.csv")       # id, title, genres
ratings = pd.read_csv("ratings.csv")     # userId, movieId, rating

# ===== 2. Content-based =====
# Lấy danh sách các cột thể loại (từ cột thứ 5 trở đi)
genre_cols = movies.columns[5:]

# Tạo cột 'genres' bằng cách ghép tên thể loại có giá trị 1
def combine_genres(row):
    return ' '.join([genre for genre in genre_cols if row[genre] == 1])

movies['genres'] = movies.apply(combine_genres, axis=1)

# TF-IDF trên genres
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])

cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)


# ===== 3. Collaborative Filtering =====
reader = Reader(rating_scale=(0.5, 5.0))
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
svd = SVD()
trainset = data.build_full_trainset()
svd.fit(trainset)

# ===== 4. Save models =====
with open("models/tfidf_matrix.pkl", "wb") as f:
    pickle.dump(tfidf_matrix, f)
with open("models/cosine_sim.pkl", "wb") as f:
    pickle.dump(cosine_sim, f)
with open("models/svd_model.pkl", "wb") as f:
    pickle.dump(svd, f)

movies.to_csv("models/movies.csv", index=False)
print("Model training complete.")
