from django.db import migrations

def convert_links(apps, schema_editor):
    Movie = apps.get_model("recommendations", "Movie")
    Episode = apps.get_model("recommendations", "Episode")

    # Update Movie trailers
    for movie in Movie.objects.all():
        if movie.trailer_link and "watch?v=" in movie.trailer_link:
            movie.trailer_link = movie.trailer_link.replace("watch?v=", "embed/")
            movie.save()

    # Update Episode links
    for ep in Episode.objects.all():
        if ep.link and "watch?v=" in ep.link:
            ep.link = ep.link.replace("watch?v=", "embed/")
            ep.save()

class Migration(migrations.Migration):

    dependencies = [
        ("recommendations", "0003_movie_tmdb_id"),  # đổi lại đúng migration trước đó
    ]

    operations = [
        migrations.RunPython(convert_links),
    ]
