from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    pub_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Post
        fields = (
            'title',
            'text',
            'location',
            'image',
            'category',
            'pub_date',
            'is_published',
        )


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
