from django import forms
from .models import Movie
from .models import Director

class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ["name", "avatar", "birthday", "description"]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập tên đạo diễn"}),
            "avatar": forms.URLInput(attrs={"class": "form-control", "placeholder": "Dán link ảnh avatar"}),
            "birthday": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Giới thiệu ngắn về đạo diễn"}),
        }

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            "name", "release_year", "description", "poster",
            "views", "rating", "status", "price",
            "country", "genres", "director", "actors"
        ]


