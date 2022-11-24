from datetime import date, datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from blog.models import *
from account.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from blog.forms import CreateCategory, CreatePost, CreateComment, CreateReply
# Create your views here.

def index(request):
    context = {}  
    if request.user.is_authenticated:
        post_list = Post.objects.filter(author=request.user).order_by('-create_date')
        post_create = Post.objects.order_by('-create_date')
        post_hits = Post.objects.order_by('-hits')
    else:
        sorting = request.GET.get('sort', '')
        if sorting == 'create_date':
            post_list = Post.objects.order_by('-create_date')
        elif sorting == 'hits':
            post_list = Post.objects.order_by('-hits')
        # elif sorting == 'voter':
        #     post_list = Post.objects.order_by('-voter')
        else :
            post_list = Post.objects.order_by('-create_date')
    context = {'post_list':post_list}

    return render(request, 'blog/index.html', context)

@login_required(login_url='login')
def create_category(request):
    if request.method == 'POST':
        form = CreateCategory(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = request.user
            category.save()
            return redirect('index')
    else:
        form = CreateCategory()
    return render(request, 'blog/create_category.html',{'form': form})
        


@login_required(login_url='login')
def update_category(request,nickname,category_name):
    category = get_object_or_404(Category, name=category_name)
    user = get_object_or_404(User, nickname=nickname)
    if request.method == 'POST':
        form = CreateCategory(request.POST,instance=category)
        
        if form.is_valid():
            category = form.save(commit=False)
            category.author = request.user
            category.modify_date = timezone.now()
            category.save()
            return redirect('index')
    else:
        form = CreateCategory(instance =category)
    return render(request, 'blog/update_category.html',{'form': form})


@login_required(login_url='login')
def delete_category(request,nickname,category_name):
    if request.user.is_authenticated:
        category = get_object_or_404(Category, name=category_name)
        user = get_object_or_404(User, nickname=nickname)
        if request.user == category.author:
            category.delete()
    return redirect('index')





# post
# -----------------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def post_vote(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        if post.voter.filter(id=request.user.id).exists():
            post.voter.remove(request.user)
        else:
            post.voter.add(request.user)
        return redirect('detail_post',post_id=post_id)
    return redirect('accounts:login')


def view_posts(request, nickname, category_name):
    category = get_object_or_404(Category, name=category_name)
    user = get_object_or_404(User, nickname=nickname)
    post_list = Post.objects.filter(author=user, category=category)
    return render(request, 'blog/view_posts.html', {'post_list': post_list, 'category': category})


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = CreatePost(request.user, request.POST)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('detail_post', post_id=post.id)
    else:
        form = CreatePost(request.user)
    return render(request, 'blog/create_post.html', {'form': form})

@login_required(login_url='login')
def update_post(request,post_id):
    post = Post.objects.get(id=post_id)
    if request.method == 'POST':
        form = CreatePost(request.user, request.POST,instance=post)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.modify_date = timezone.now()
            post.save()
            return redirect('detail_post', post_id=post.id)
    else:
        form = CreatePost(request.user,instance =post)
    return render(request, 'blog/update_post.html',{'form': form})


@login_required(login_url='login')
def delete_post(request, post_id):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=post_id)
        if request.user == post.author:
            post.delete()
    return redirect('index')


def detail_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comment_form = CreateComment()
    reply_form = CreateReply()
    
    response = render(request, 'blog/detail_post.html', {'post': post, 'comment_form': comment_form, 'reply_form': reply_form})
    # 조회수 기능은 쿠키를 이용하는데 쿠키에 열람한 게시글에 관한 데이터를 넣음
    # 쿠키는 만료기간을 조절하는 것으로 조회수 증가 기준을 정함
    expire_date, now = datetime.now(), datetime.now()
    expire_date += timedelta(days=1)
    expire_date = expire_date.replace(hour=0, minute=0, second=0, microsecond=0)
    expire_date -= now
    max_age = expire_date.total_seconds()

    cookie_value = request.COOKIES.get('hitblog', '_')

    if f'_{id}_' not in cookie_value:
        cookie_value += f'{id}_'
        response.set_cookie('hitblog', value=cookie_value, max_age=max_age, httponly=True)
        post.hits += 1
        post.save()
    return response

# comment
# -----------------------------------------------------------------------------------------------------------------------------------------------
@login_required(login_url='login')
def create_comment(request):
    post = get_object_or_404(Post, pk=request.GET.get('post_id', None))
    if request.method == 'POST':
        form = CreateComment(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('detail_post', post_id=post.id)
    else:
        form = CreateComment()
    return redirect('detail_post', {'form': form})

@login_required(login_url='login')
def update_comment(request,comment_id):
    comment = get_object_or_404(Comment,id=comment_id)
    post = comment.post
    if request.method == 'POST':
        form = CreateComment(request.POST,instance=comment)
        
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.save()
            return redirect('detail_post', post_id=post.id)
    else:
        form = CreateComment(instance =comment)
    context = {'comment':comment, 'form':form}
    return redirect('detail_post',context)


@login_required(login_url='login')
def delete_comment(request,comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(Comment,id=comment_id)
        post = comment.post
        if request.user == comment.author:
            comment.delete()
        return redirect('detail_post',post_id=post.id)


#reply
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
@login_required(login_url='login')
def create_reply(request):
    comment = get_object_or_404(Comment, pk=request.GET.get('comment_id', None))
    if request.method == "POST":
        form = CreateReply(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
            return redirect('detail_post', post_id=comment.post.id)
    else:
        form = CreateReply()
    context = {'form':form}
    return redirect('detail_post',context)

@login_required(login_url='login')
def delete_reply(request,reply_id):
    if request.user.is_authenticated:
        reply = Reply.objects.get(id=reply_id)
        comment = reply.comment
        post = reply.comment.post
        if request.user == reply.author:
            reply.delete()
    return redirect('detail_post',post_id=post.id)