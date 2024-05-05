from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostSuccessURLMixin():

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']})


class ProfileSuccessURLMixin():

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username})
