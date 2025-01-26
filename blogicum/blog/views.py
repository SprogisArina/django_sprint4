from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post

POSTS_ON_DIPLAY = 10
User = get_user_model()
post_queryset = Post.objects.select_related(
    'author', 'category', 'location'
).filter(
    pub_date__lte=timezone.now(),
    is_published=True,
    category__is_published=True
)


class UserDetailView(DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = User
        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = 'blog:profile'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.created_at = timezone.now()
        form.instance.is_published = True
        return super().form_valid(form)


class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = 'blog:profile'


class CommentCreateView(CreateView):
    post = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post.post_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.post.pk})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class Index(ListView):
    model = Post
    queryset = post_queryset
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'


# class CategoryListView(ListView):
#     model = Category


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
