from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .models import Post


def filter_posts(
        model_manager=Post.objects,
        filter_flag=False,
        author_filter_flag=False,
        annotation_flag=False,
        username=None):
    """
    Функция для фильтрации постов
    filter_flag=True - фильтр скрытых и отложенных постов,
    скрытых категорий
    author_filter_flag=True - фильтр постов определенного автора
    annotation_flag=True - добавление количества комментриев
    """
    queryset = model_manager.select_related(
        'author', 'category', 'location'
    )
    if filter_flag:
        queryset = queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
    if author_filter_flag:
        queryset = queryset.filter(
            author__username=username
        )
    if annotation_flag:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return queryset


def paginate_posts(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_ON_DIPLAY)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
