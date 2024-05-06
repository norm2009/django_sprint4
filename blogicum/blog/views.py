from datetime import datetime, timezone

from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http.response import Http404
from django.shortcuts import redirect
from django.views.generic import (
    UpdateView,
    ListView,
    CreateView,
    DeleteView,
    DetailView)
from django.contrib.auth import get_user_model

from blog.forms import ProfileForm, PostForm, CommentForm
from blog.models import Post, Category, Comment
from blog.mixins import (
    OnlyAuthorMixin,
    PostSuccessURLMixin,
    ProfileSuccessURLMixin)
import blog.constants as const


User = get_user_model()


def annotate_comment_count(qs):
    return qs.annotate(comment_count=Count('comment')).order_by('-pub_date')


def qs_filter_list_view(qs, **kwargs):
    return annotate_comment_count(
        qs.filter(
            **kwargs,
            pub_date__lt=datetime.now(tz=timezone.utc),
            is_published=True))


class PostsListView(ListView):

    model = Post
    ordering = ['-pub_date']
    paginate_by = const.POSTS_AT_PAGE


class PostCreateView(ProfileSuccessURLMixin, LoginRequiredMixin, CreateView):

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostDetailView(UserPassesTestMixin, DetailView):

    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (Comment.objects.filter(
            post=self.kwargs['post_id']))
        return context

    def test_func(self):
        object = self.get_object()
        return (object.author == self.request.user
                or (object.is_published and object.category.is_published))

    def handle_no_permission(self):
        raise Http404


class PostUpdateView(PostSuccessURLMixin, OnlyAuthorMixin, UpdateView):

    pk_url_kwarg = 'post_id'
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            post_id=self.kwargs['post_id'])


class IndexListView(PostsListView):

    template_name = 'blog/index.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs_filter_list_view(qs, category__is_published=True)


class CategoryListView(PostsListView):

    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True)
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs_filter_list_view(
            qs,
            category__slug=self.kwargs['category_slug'])


class ProfileListView(PostsListView):

    template_name = 'blog/profile.html'
    pk_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.username == self.kwargs['username']:
            return annotate_comment_count(
                qs.filter(
                    author__username=self.kwargs['username']))
        return qs_filter_list_view(
            qs,
            category__is_published=True,
            author__username=self.kwargs['username'])


class CommentCreateView(PostSuccessURLMixin, LoginRequiredMixin, CreateView):

    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)


class CommentUpdateView(PostSuccessURLMixin, OnlyAuthorMixin, UpdateView):

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def handle_no_permission(self):
        raise Http404


class ProfileUpdateView(
        ProfileSuccessURLMixin,
        LoginRequiredMixin,
        UpdateView):

    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user


class CommentDeleteView(PostSuccessURLMixin, OnlyAuthorMixin, DeleteView):

    model = Comment
    template_name = 'blog/comment.html'

    def handle_no_permission(self):
        raise Http404


class PostDeleteView(ProfileSuccessURLMixin, OnlyAuthorMixin, DeleteView):

    pk_url_kwarg = 'post_id'
    model = Post
    template_name = 'blog/create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
