from django.urls import include, path

from . import views

app_name = 'blog'

comment_urls = [
    path('comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
]

post_urls = [
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path('<int:post_id>/edit/', views.PostUpdateView.as_view(),
         name='edit_post'),
    path('<int:post_id>/delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('<int:post_id>/', include(comment_urls)),
    path('<int:post_id>/', views.PostDetailView.as_view(),
         name='post_detail'),
]

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('posts/', include(post_urls)),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<username>/', views.get_user_detail,
         name='profile')
]
