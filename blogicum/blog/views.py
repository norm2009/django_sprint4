from datetime import datetime, timezone

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import UpdateView, ListView, CreateView, DeleteView
from django.contrib.auth import get_user_model

from blog.forms import ProfileForm, PostForm, CommentForm
from blog.models import Post, Category, Comment
import blog.constants as const


User = get_user_model()


def posts_filter(*args, **kwargs):
    return Post.objects.select_related(
        *args,
        'location',
        'author',
        'category'
    ).filter(
        **kwargs,
        is_published=True,
        category__is_published=True,
        pub_date__lt=datetime.now(tz=timezone.utc)
    )


def index(request):
    template = 'blog/index.html'
    posts = (
        posts_filter()
    )
    paginator = Paginator(posts, const.POSTS_AT_PAGE)
    page_number = request.GET.get('page')
    context = {'page_obj': paginator.get_page(page_number)}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.values(
            'title',
            'description',
            'id'
        ).filter(
            slug=category_slug,
            is_published=True
        )
    )
    posts = (
        posts_filter(category=category.get('id'))
    )
    paginator = Paginator(posts, const.POSTS_AT_PAGE)
    page_number = request.GET.get('page')
    context = {'category': category,
               'page_obj': paginator.get_page(page_number)}
    return render(request, template, context)


class ProfileListView(ListView, LoginRequiredMixin):
    model = Post
    ordering = ['-pub_date']
    template_name = 'blog/profile.html'
    paginate_by = const.POSTS_AT_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'])
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.username == self.kwargs['username']:
            return qs.filter(author__username=self.kwargs['username'])
        return qs.filter(author__username=self.kwargs['username'],
                         pub_date__lt=datetime.now(tz=timezone.utc))


def post_detail(request, id):
    template = 'blog/detail.html'
    posts = get_object_or_404(
        posts_filter(id=id)
    )
    context = {'post': posts}
    return render(request, template, context)


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['comments'] = Comment.objects.filter(post=self.kwargs['pk'])
        return context


class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['comment_id'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['pk']})


class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.object.username})

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.pk)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['pk']})


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})
