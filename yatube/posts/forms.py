from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        widget = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widget = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Введите комментарий',
        }
