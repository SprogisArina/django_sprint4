from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post

# Количество выводимых на главную страницу постов
POSTS_ON_DIPLAY = 5


def filter_posts():
    return Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    post_list = filter_posts()[:POSTS_ON_DIPLAY]
    return render(request, 'blog/index.html', {'post_list': post_list})


def post_detail(request, post_id):
    post = get_object_or_404(filter_posts(), pk=post_id)
    return render(request, 'blog/detail.html', {'post': post})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, is_published=True, slug=category_slug
    )
    post_list = filter_posts().filter(category__slug=category_slug)
    context = {
        'category': category,
        'post_list': post_list
    }
    return render(request, 'blog/category.html', context)
