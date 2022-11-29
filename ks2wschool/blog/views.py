from datetime import date, datetime, timedelta
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Count
from django.core import serializers

from account.models import User
from blog.models import *
from blog.forms import CreateCategory, CreatePost, CreateComment, CreateReply
from blog.models import *

# Create your views here.

def index(request):
    context = {}  
    sorting = request.GET.get('sort', '')
    if sorting == 'hits':
        post_list = Post.objects.order_by('-hits', '-create_date')
    elif sorting == 'voter':
        post_list = Post.objects.annotate(like_count=Count('voter')).order_by('-like_count', '-create_date')
    else:
        post_list = Post.objects.order_by('-create_date')

    page = request.GET.get('page', '1')
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page)
    context = {'post_list': page_obj}
    return render(request, 'blog/index.html', context) 

@login_required(login_url='login')
def update_category(request,nickname,category_name):
    print(request.user.nickname)
    print(nickname)
    if request.user.nickname == nickname:
        category = get_object_or_404(Category, name=category_name, author=request.user)
        if request.method == 'POST':
            form = CreateCategory(request.POST,instance=category)
            if form.is_valid():
                category = form.save(commit=False)
                category.modify_date = timezone.now()
                category.save()
                return redirect('index')
        else:
            form = CreateCategory(instance =category)
        return render(request, 'blog/update_category.html',{'form': form})
    else:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('view_posts', nickname=nickname, category_name=category_name)


@login_required(login_url='login')
def delete_category(request,nickname,category_name):
    if request.user.nickname == nickname:
        user = get_object_or_404(User, nickname=nickname)
        category = get_object_or_404(Category, name=category_name, author=user)
        if request.user == category.author:
            category.delete()
    else:
        messages.error(request, '삭제 권한이 없습니다.')
    return redirect('index')





# post
# -----------------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url='login')
def post_vote(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.voter.filter(id=request.user.id).exists():
        post.voter.remove(request.user)
    else:
        post.voter.add(request.user)
    return redirect('detail_post',post_id=post_id)
    return redirect('accounts:login')


def view_posts(request, nickname, category_name):
    user = get_object_or_404(User, nickname=nickname)
    category = get_object_or_404(Category, name=category_name, author=user)
    post_list = Post.objects.filter(author=user, category=category)
    return render(request, 'blog/view_posts.html', {'post_list': post_list, 'category': category , 'author': user})


@login_required(login_url='login')
def create_post(request):
    user = User.objects.get(nickname=request.user)
    if request.user.nickname == user.nickname:
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
    else:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('index')


@login_required(login_url='login')
def update_post(request,post_id):
    post = Post.objects.get(id=post_id)
    if request.user.nickname == post.author.nickname:
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
    else:
        messages.error(request, '수정 권한이 없습니다.')
    return redirect('detail_post',post_id = post.id)


@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    user = post.author
    if request.user.nickname == user.nickname:
        if request.user.is_authenticated:
        
            if request.user == post.author:
                post.delete()
        return redirect('index')
    else:
        messages.error(request, '삭제 권한이 없습니다.')
    return redirect('detail_post',post_id=post.id)

def post_list(request, nickname):
    user = get_object_or_404(User, nickname=nickname)
    sorting = request.GET.get('sort', '')

    if sorting == 'hits':
        post_list = user.post_set.all().order_by('-hits','-create_date')
    elif sorting == 'voter':
        post_list = user.post_set.all().annotate(like_count=Count('voter')).order_by('-like_count', '-create_date')
    else:
        post_list = user.post_set.all().order_by('-create_date')
    return render(request, 'blog/post_list.html', {'post_list': post_list, 'author': user
    ,'sorting':sorting})


def detail_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    response = render(request, 'blog/detail_post.html', {'post': post})
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
    print(request.GET.get('post_id'))
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
    return redirect('detail_post', post_id=post.id)

@login_required(login_url='login')
def update_comment(request,comment_id):
    comment = get_object_or_404(Comment,id=comment_id)
    post = comment.post
    if request.user.nickname == comment.author.nickname:
        if request.method == 'POST':
            form = CreateComment(request.POST,instance=comment)
            
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.modify_date = timezone.now()    
                comment.save()
                return redirect('detail_post', post_id=post.id)
        else:
            form = CreateComment()
            context = {'form':form}
        return redirect('detail_post',context)
    else:
        messages.error(request, '수정 권한이 없습니다.')
    return redirect('detail_post',post_id=post.id)


@login_required(login_url='login')
def delete_comment(request,comment_id):
    comment = get_object_or_404(Comment,id=comment_id)
    if request.user.nickname == comment.author.nickname:    
        post = comment.post
        if request.user == comment.author:
            comment.delete()
        return redirect('detail_post',post_id=post.id)
    else:
         messages.error(request, '삭제 권한이 없습니다.')
    return redirect('detail_post',post_id=post.id)


#reply
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# @login_required(login_url='login')
# def create_reply(request):
#     comment = get_object_or_404(Comment, pk=request.GET.get('comment_id', None))
#     if request.method == "POST":
#         form = CreateReply(request.POST)
#         if form.is_valid():
#             reply = form.save(commit=False)
#             reply.comment = comment
#             reply.author = request.user
#             reply.save()
#             return redirect('detail_post', post_id=comment.post.id)
#     else:
#         form = CreateReply()
#     context = {'form':form}
#     return redirect('detail_post',context)

@login_required(login_url='login')
def create_reply(request):
    comment = get_object_or_404(Comment, pk=request.GET.get('comment_id'))
    if request.method == 'POST':
        form = CreateReply(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.comment = comment
            reply.save()
            return JsonResponse({"flag": True})
        else:
            err = {"error": "입려값이 없습니다."}
    else:
        err = {"error": "잘못된 접근 방식입니다."}
    err.update({"flag": False})
    return JsonResponse(err)

@login_required(login_url='login')
def delete_reply(request,reply_id):
    reply = Reply.objects.get(id=reply_id)
    comment = reply.comment
    post = reply.comment.post
    if request.user.nickname == reply.author.nickname:
        if request.user == reply.author:
            reply.delete()
    else:
        messages.error(request, '삭제 권한이 없습니다.')
    return redirect('detail_post',post_id=post.id)

def user_search(request):
    search_val = request.GET.get('search_val')
    print(search_val)
    user_list = User.objects.all()
    if search_val:
        user_list = user_list.filter(
            Q(nickname__icontains=search_val)
        ).distinct()
    user_list = [user.nickname for user in user_list]
    return JsonResponse({"user_list" : user_list})

@login_required(login_url='login')
def create_category(request):
    if request.method == 'POST':
        form = CreateCategory(request.POST)
        if form.is_valid():
            if Category.objects.filter(name=form.cleaned_data['name'], author=request.user).count() > 0:
                err = {"error": '이미 카테고리가 있습니다.'}
            else:
                category = form.save(commit=False)
                category.author = request.user
                category.save()
                return JsonResponse({"flag": True})
        else:
            err = {"error": '입력값이 없습니다.'}
    else:
        err = {"error": '제한된 접근입니다.'}
    err.update({"flag": False})
    return JsonResponse(err)

def view_reply(request):
    comment_id = request.GET.get('comment_id')
    comment = get_object_or_404(Comment, pk=comment_id)
    reply_list = comment.reply_set.all()
    data = {'reply': [{'id': reply.id, 'content': reply.content, 'author': reply.author.nickname, 'create_date': reply.create_date, 'modify_date': reply.modify_date} for reply in reply_list]}
    data.update({'comment': {'content': comment.content, 'author': comment.author.nickname, 'create_date': comment.create_date, 'modify_date': comment.modify_date}})
    return JsonResponse(data)