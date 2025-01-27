from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import CommentForm, PostForm
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
    )


# class CommentMixin:
#     model = Comment
#     post_field = None

#     def dispatch(self, request, *args, **kwargs):
#         self.post_field = get_object_or_404(Post, pk=kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)

#     def get_success_url(self):
#         return reverse('blog:post_detail', kwargs={'pk': self.post_field.pk})


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
    success_url = reverse_lazy('blog:profile')

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


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.all()
        )
        return context


class CommentCreateView(CreateView):
    post_field = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_field = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.post_field
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_field.pk})


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail')


class CommentDeleteView(DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_field.pk})


class Index(ListView):
    model = Post
    queryset = filter_posts()
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'


# def index(request):
#     post_list = filter_posts()[:POSTS_ON_DIPLAY]
#     return render(request, 'blog/index.html', {'post_list': post_list})


# def post_detail(request, post_id):
#     post = get_object_or_404(filter_posts(), pk=post_id)
#     return render(request, 'blog/detail.html', {'post': post})


def get_user_detail(request, username):
    post_list = filter_posts().filter(author=username)
    profile = get_object_or_404(User, username=username)
    context = {
        'page_obj': post_list,
        'profile': profile,
    }
    return render(request, 'blog/profile.html', context)


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
