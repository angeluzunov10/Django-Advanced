from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory

from forumApp.posts.mixins import DisableFieldsMixin
from forumApp.posts.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ['approved',]

        error_messages = {
            'title': {
                'required': 'Please enter a title of your post.',
                'max_length': f'The title is too long. Please keep it under {Post.TITLE_MAX_LENGTH} characters.'
            }
        }

    def clean_author(self):
        author = self.cleaned_data.get('author')

        if author[0] != author[0].upper():
            raise ValidationError('Author name must start with a capital letter!')

        return author

    def clean(self):
        cleaned_data = super().clean()

        title = cleaned_data.get('title')
        content = cleaned_data.get('content')

        if title and content and title in content:
            raise ValidationError('The post title cannot be included in the post content!')

        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)

        post.title = post.title.capitalize()

        if commit:
            post.save()

        return post


class PostCreateForm(PostForm):
    pass


class PostEditForm(PostForm):
    pass


class PostDeleteForm(PostForm, DisableFieldsMixin):
    disabled_fields = ('__all__',)


class SearchForm(forms.Form):
    query = forms.CharField(
        label='',
        required=False,
        max_length=5,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Search for a specific post...',
            }
        )
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'content')

        labels = {
            'author': '',
            'content': '',
        }

        error_messages = {
            'author': {
                'required': 'Author name is required!',
            },
            'content': {
                'required': 'Content is required!',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['author'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your name',
        })

        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Add message...',
        })


CommentFormSet = formset_factory(CommentForm, extra=1)