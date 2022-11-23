from blog.models import *
from django import forms

class CreatePost(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(CreatePost, self).__init__(*args, **kwargs) # populates the post
        self.fields['category'].queryset = Category.objects.filter(author=user)

    class Meta:
        model = Post
        fields = ['category','title', 'content']
        labels = {
            'category' : '카테고리',
            'title' : '제목',
            'content' : '내용',
        }


class CreateCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'author']
        labels = {
            'name':'카테고리 이름',
        }


class CreateComment(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content' : '댓글 쓰기'
        }

class CreateReply(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        labels = {
            'content' : '답글 쓰기'
        }