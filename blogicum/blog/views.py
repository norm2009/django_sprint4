from datetime import datetime, timezone

from django.core.paginator import Paginator
#from django.utils import timezone
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse

from django.views.generic import DetailView, TemplateView, UpdateView, ListView, CreateView
from django.contrib.auth import get_user_model

from blog.forms import ProfileForm, PostForm
from blog.models import Post, Category
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


def post_detail(request, id):
    template = 'blog/detail.html'
    posts = get_object_or_404(
        posts_filter(id=id)
    )
    context = {'post': posts}
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
               'post_list': paginator.get_page(page_number)}
    return render(request, template, context)


class ProfileListView(ListView, LoginRequiredMixin):
    model = Post
    ordering = ['-pub_date']
    template_name = 'blog/profile.html'
    paginate_by = const.POSTS_AT_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(User, username=self.kwargs['username'])
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author__username=self.kwargs['username'])


class ProfileUpdateView(UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.object.username})

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.pk)

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.pub_date = datetime.now(tz=timezone.utc)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user.username})

