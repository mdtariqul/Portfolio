from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("projects/<slug:slug>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("blog/<slug:slug>/", views.BlogDetailView.as_view(), name="blog-detail"),
    path("contact/", views.contact, name="contact"),
    path("resume/", views.resume_download, name="resume"),
]
