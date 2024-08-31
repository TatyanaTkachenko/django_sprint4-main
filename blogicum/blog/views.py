from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import Now
from django.core.paginator import Paginator

from .constants import POSTS_LIMIT
from .forms import PostForm, EditUserForm, CommentForm
from .models import Category, Post, Comment, User


def get_posts(post_objects):
    return post_objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=Now()
    ).annotate(comment_count=Count('comments'))


def pagination(items, num_pages=POSTS_LIMIT):
    return Paginator(items, num_pages).get_page(num_pages)


@login_required
def create_post(request):
    template = 'blog/create.html'
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)

    if request.method == "POST":
        form = PostForm(
            request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            post.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_profile(request):
    template = 'blog/user.html'
    form = EditUserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        post.delete()
        return redirect('blog:index')
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form, 'comment': comment}
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, template, context)


def index(request):
    post_list = get_posts(
        Post.objects
    ).order_by('-pub_date')[:POSTS_LIMIT]
    template = 'blog/index.html'
    page_obj = pagination(post_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        get_posts(Post.objects) | request.user.posts.all(), id=post_id)
    comments = Comment.objects.select_related('post', 'author').filter(
        is_published=True, post=post)
    form = CommentForm()
    context = {'post': post, 'form': form, 'comments': comments}
    return render(request, template, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_posts(category.posts).order_by('-pub_date')
    template = 'blog/category.html'
    page_obj = pagination(post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


def profile(request, username):
    template = 'blog/profile.html'
    user = get_object_or_404(User, username=username)
    posts_list = user.posts.annotate(
        comment_count=Count('comments')).order_by(
        '-pub_date'
    )
    page_obj = pagination(posts_list)
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, template, context)
