import pandas as pd

# ==================== Ratings ====================
ratings_cols = ['userId', 'movieId', 'rating', 'timestamp']
ratings = pd.read_csv('ml-100k/u.data', sep='\t', names=ratings_cols)
ratings.to_csv('ratings.csv', index=False)
print("ratings.csv đã tạo xong")
print(ratings.head(), "\n")

# ==================== Movies ====================
movie_cols = [
    'movieId', 'title', 'release_date', 'video_release_date', 'imdb_url',
    'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
    'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

movies = pd.read_csv('ml-100k/u.item', sep='|', names=movie_cols, encoding='latin-1')
movies.to_csv('movies.csv', index=False)
print("movies.csv đã tạo xong")
print(movies.head())
