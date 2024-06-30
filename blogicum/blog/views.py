from django.db.models.functions import Now
from django.shortcuts import get_object_or_404, render

from . import constants
from .models import Category, Post


def get_posts(post_objects):
    return post_objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=Now()
    )


def index(request):
    post_list = get_posts(
        Post.objects
    )[:constants.POSTS_LIMIT]
    template = 'blog/index.html'
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        get_posts(Post.objects) | request.user.posts.all(), id=post_id)
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_posts(category.posts)
    template = 'blog/category.html'
    context = {'category': category, 'post_list': post_list}
    return render(request, template, context)
