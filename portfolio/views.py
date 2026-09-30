from django.conf import settings
from django.contrib import messages
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, TemplateView

from .models import BlogPost, ContactMessage, Education, Experience, Profile, Project, Skill


class HomeView(TemplateView):
    template_name = "portfolio/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = Profile.objects.first()
        ctx["education"] = Education.objects.all()
        ctx["experiences"] = Experience.objects.all()
        ctx["projects"] = Project.objects.prefetch_related("technologies").all()
        ctx["posts"] = BlogPost.objects.filter(is_published=True)[:6]
        # Group skills by category for sectioned display
        skills = Skill.objects.all()
        grouped = {}
        for s in skills:
            grouped.setdefault(s.get_category_display(), []).append(s)
        ctx["skill_groups"] = grouped
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = "portfolio/project_detail.html"
    slug_field = "slug"


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = "portfolio/blog_detail.html"
    slug_field = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


def contact(request):
    if request.method != "POST":
        return redirect("home")
    name = request.POST.get("name", "").strip()[:120]
    email = request.POST.get("email", "").strip()[:254]
    message = request.POST.get("message", "").strip()[:2000]
    if not (name and email and message):
        messages.error(request, "Please fill in all fields.")
        return redirect("home")
    ContactMessage.objects.create(name=name, email=email, message=message)
    messages.success(request, "Thanks! Your message has been received.")
    return redirect("home")


def resume_download(request):
    path = settings.BASE_DIR / "resume.md"
    return FileResponse(
        open(path, "rb"),
        as_attachment=True,
        filename="Tariqul-Islam-Resume.md",
        content_type="text/markdown",
    )
