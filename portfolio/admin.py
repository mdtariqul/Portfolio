from django.contrib import admin
from .models import BlogPost, ContactMessage, Course, Education, Experience, Profile, Project, Skill


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "title", "updated_at"]


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ["degree", "institution", "order"]


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["role", "company", "is_current", "order"]
    list_editable = ["order"]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "proficiency", "order"]
    list_filter = ["category"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "featured", "order"]
    list_editable = ["order", "featured"]
    prepopulated_fields = {"slug": ["title"]}
    filter_horizontal = ["technologies"]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "provider", "order"]
    list_editable = ["order"]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ["title", "is_published", "published_at"]
    list_filter = ["is_published"]
    prepopulated_fields = {"slug": ["title"]}


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "read", "created_at"]
    readonly_fields = ["name", "email", "message", "created_at"]
