from django.views.generic import TemplateView
from django.shortcuts import render
from http import HTTPStatus


class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    template_name = 'pages/rules.html'


def csrf_failure(request, reason=''):
    return render(
        request,
        'pages/403csrf.html',
        status=HTTPStatus.FORBIDDEN)


def page_not_found(request, exception):
    return render(
        request,
        'pages/404.html',
        status=HTTPStatus.NOT_FOUND)


def e_handler500(request, *args, **kwargs):
    return render(
        request,
        'pages/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR)
