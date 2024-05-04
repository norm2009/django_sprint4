from datetime import datetime, timezone

from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.http.response import Http404
from django.shortcuts import redirect
from django.views.generic import UpdateView, ListView, CreateView, DeleteView, DetailView
from django.contrib.auth import get_user_model

from blog.forms import ProfileForm, PostForm, CommentForm
from blog.models import Post, Category, Comment
import blog.constants as const


User = get_user_model()


class PostsListView(ListView):
    model = Post
    ordering = ['-pub_date']
    paginate_by = const.POSTS_AT_PAGE

class PostCreateView(LoginRequiredMixin, CreateView):

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                       kwargs={'username': self.request.user.username})

class PostDetailView(UserPassesTestMixin, DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            Comment.objects.filter(
                post=self.kwargs['post_id']).order_by('created_at')
        )
        return context

    def test_func(self):
        object = self.get_object()
        print(object.author, self.request.user, (
                not object.is_published or not object.category.is_published))
        if object.author != self.request.user and (
                not object.is_published or not object.category.is_published):
            return False
        return True

    def handle_no_permission(self):
        raise Http404

class PostUpdateView(UserPassesTestMixin, UpdateView):
    pk_url_kwarg = 'post_id'
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})

class IndexListView(PostsListView):
    template_name = 'blog/index.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(pub_date__lt=datetime.now(tz=timezone.utc),
                         is_published=True,
                         category__is_published=True).\
            annotate(comment_count=Count('comment'))


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
        return qs.filter(pub_date__lt=datetime.now(tz=timezone.utc),
                         is_published=True,
                         category__slug=self.kwargs['category_slug']). \
            annotate(comment_count=Count('comment'))


class ProfileListView(PostsListView):

    template_name = 'blog/profile.html'
    pk_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        return context
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.username == self.kwargs['username']:
            return qs.filter(author__username=self.kwargs['username']).\
                annotate(comment_count=Count('comment'))
        return qs.filter(author__username=self.kwargs['username'],
                         pub_date__lt=datetime.now(tz=timezone.utc),
                         category__is_published=True,
                         is_published=True,).\
            annotate(comment_count=Count('comment'))


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'
    # pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})



class CommentUpdateView(UpdateView):

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model,
                                 pk=self.kwargs['comment_id'],
                                 author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                       kwargs={'username': self.object.username})

    def get_object(self):
        return self.request.user









    # def dispatch(self, request, *args, **kwargs):
    #     self.post = get_object_or_404(
    #         Post, pk=self.kwargs[self.pk_url_kwarg])
    #     if self.post.author != self.request.user and (
    #             not self.post.is_published
    #             or not self.post.category.is_published):
    #         raise Http404
    #     return super().dispatch(request, *args, **kwargs)

    # def get_object(self):
    #     return self.post

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostDeleteView(UserPassesTestMixin, DeleteView):
    pk_url_kwarg = 'post_id'
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
