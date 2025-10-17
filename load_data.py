import ssl
import tensorflow_datasets as tfds

# Bỏ qua SSL verify
ssl._create_default_https_context = ssl._create_unverified_context

# Load ratings dataset
ratings = tfds.load('movielens/100k-ratings', split='train')

# Load movies dataset
movies = tfds.load('movielens/100k-movies', split='train')

# Xem thử vài dòng dữ liệu
for example in ratings.take(3):
    print(example)
