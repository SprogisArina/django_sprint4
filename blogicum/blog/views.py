from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post

POSTS_ON_DIPLAY = 10
User = get_user_model()


def filter_posts():
    return Post.objects.select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


class PostMixin:
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'


class CommentMixin:
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.created_at = timezone.now()
        form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user}
        )


class PostUpdateView(
        PostMixin,
        UpdateView):
    form_class = PostForm

    def form_valid(self, form):
        if self.request.user != self.object.author:
            return redirect(
                'blog:post_detail', post_id=self.kwargs['post_id']
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.object.pk)
        form = PostForm(instance=instance)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user}
        )


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_object(self, queryset=filter_posts()):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.all()
        )
        return context


class CommentCreateView(CommentMixin, LoginRequiredMixin, CreateView):
    model = Comment
    post_field = None
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_field = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_field
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.object.post_id}
        )


class Index(ListView):
    model = Post
    queryset = filter_posts()
    paginate_by = 10
    template_name = 'blog/index.html'


def get_user_detail(request, username):
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        post_list = Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            author__username=username
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    else:
        post_list = filter_posts().filter(author__username=username)
    paginator = Paginator(post_list, POSTS_ON_DIPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'profile': profile,
    }
    return render(request, 'blog/profile.html', context)


def edit_profile(request):
    profile = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', {'form': form})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, is_published=True, slug=category_slug
    )
    post_list = filter_posts().filter(category__slug=category_slug)
    paginator = Paginator(post_list, POSTS_ON_DIPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)
