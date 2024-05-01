from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/',
         views.post_detail,
         name='post_detail'),
    path('posts/<int:id>/edit',
         views.post_detail,
         name='edit_post'),
    path('posts/<post_id>/delete/',
         views.post_detail,
         name='delete_post'),
    path('posts/<post_id>/comment',
         views.post_detail,
         name='add_comment'),
    path('posts/<post_id>/delete_comment/<comment_id>/',
         views.post_detail,
         name='delete_comment'),
    path('posts/<post_id>/edit_comment/<comment_id>/',
         views.post_detail,
         name='edit_comment'),
    path('posts/create/',
         views.PostCreateView.as_view(),
         name='create'),
    path('edit_profile/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('category/<slug:category_slug>/',
         views.category_posts,
         name='category_posts'),
    path('profile/<str:username>/',
         views.ProfileListView.as_view(),
         name='profile'),
]

