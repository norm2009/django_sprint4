from django.shortcuts import render
from django.views.generic import TemplateView

class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'
# def about(request):
#     template = 'pages/about.html'
#     return render(request, template)

class RulesTemplateView(TemplateView):
    template_name = 'pages/rules.html'
# def rules(request):
#     template = 'pages/rules.html'
#     return render(request, template)
