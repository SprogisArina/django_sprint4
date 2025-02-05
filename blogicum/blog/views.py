from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm, UserForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Comment, Post
from .utils import filter_posts, paginate_posts


User = get_user_model()


class PostCreateView(PostMixin, LoginRequiredMixin, CreateView):
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostUpdateView(
        PostMixin,
        OnlyAuthorMixin,
        UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDeleteView(PostMixin, OnlyAuthorMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = PostForm(instance=self.object)
        context['form'] = form
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostDetailView(PostMixin, DetailView):
    template_name = 'blog/detail.html'

    def get_object(self, queryset=filter_posts(filter_flag=True)):
        post = get_object_or_404(filter_posts(), pk=self.kwargs['post_id'])
        if self.request.user == post.author:
            return post
        return super().get_object(queryset)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related(
                'author'
            )
        )
        return context


class CommentCreateView(CommentMixin, LoginRequiredMixin, CreateView):
    model = Comment
    post_field = None
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
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
    queryset = filter_posts(filter_flag=True, annotation_flag=True)
    paginate_by = settings.POSTS_ON_DIPLAY
    template_name = 'blog/index.html'


def get_user_detail(request, username):
    profile = get_object_or_404(User, username=username)
    if profile == request.user:
        filter_flag = False
    else:
        filter_flag = True
    post_list = filter_posts(
        model_manager=profile.posts,
        filter_flag=filter_flag,
        annotation_flag=True,
    )
    page_obj = paginate_posts(request, post_list)
    context = {
        'page_obj': page_obj,
        'profile': profile,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
    return render(request, 'blog/user.html', {'form': form})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, is_published=True, slug=category_slug
    )
    post_list = filter_posts(
        model_manager=category.posts,
        filter_flag=True,
        annotation_flag=True
    )
    page_obj = paginate_posts(request, post_list)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)
