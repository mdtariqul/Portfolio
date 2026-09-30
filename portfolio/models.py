import bleach
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

MAX_PHOTO_DIM = 1600  # longest side after normalization
MAX_UPLOAD_MB = 8


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    order = models.IntegerField(default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order", "-id"]


class Profile(TimeStampedModel):
    """Singleton: your identity, summary, photo. Only one row allowed."""

    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, help_text="e.g. R&D Engineer — Routing / Embedded Networking")
    summary = models.TextField(help_text="Personal summary shown at top of page")
    photo = models.ImageField(
        upload_to="profile/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
        help_text="Required. Square photo works best.",
    )
    location = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    leetcode_url = models.URLField(blank=True)

    def clean(self):
        if self.pk is None and Profile.objects.exists():
            raise ValidationError("Only one Profile allowed. Edit the existing one.")
        if self.photo and hasattr(self.photo, "size") and self.photo.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise ValidationError(f"Photo must be under {MAX_UPLOAD_MB}MB.")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._normalize_photo()

    def _normalize_photo(self):
        """Downscale any upload to MAX_PHOTO_DIM so portrait/landscape/square all behave."""
        from PIL import Image, ImageOps

        if not self.photo or not self.photo.storage.exists(self.photo.name):
            return
        try:
            with self.photo.storage.open(self.photo.name, "rb") as f:
                img = Image.open(f)
                img.load()
        except Exception:
            return
        img = ImageOps.exif_transpose(img)
        if max(img.size) <= MAX_PHOTO_DIM and img.mode in ("RGB", "RGBA"):
            return  # already fine
        img.thumbnail((MAX_PHOTO_DIM, MAX_PHOTO_DIM), Image.LANCZOS)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")
        buf = __import__("io").BytesIO()
        fmt = "PNG" if self.photo.name.lower().endswith(".png") else "JPEG"
        img.save(buf, format=fmt, quality=82, optimize=True)
        buf.seek(0)
        with self.photo.storage.open(self.photo.name, "wb") as f:
            f.write(buf.read())

    @property
    def has_photo(self):
        return bool(self.photo) and self.photo.storage.exists(self.photo.name)

    def get_rag_text(self):
        return f"{self.full_name}, {self.title}. {self.summary} Location: {self.location}"

    def __str__(self):
        return self.full_name


class Education(OrderedModel, TimeStampedModel):
    degree = models.CharField(max_length=200)
    institution = models.CharField(max_length=200)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    result = models.CharField(max_length=100, blank=True, help_text="e.g. CGPA 3.30/4.00")
    description = models.TextField(blank=True)

    def get_rag_text(self):
        return f"Education: {self.degree} at {self.institution} ({self.result}). {self.description}"

    def __str__(self):
        return f"{self.degree} — {self.institution}"


class Experience(OrderedModel, TimeStampedModel):
    role = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    bullets = models.TextField(help_text="One achievement per line")

    class Meta(OrderedModel.Meta):
        abstract = False

    def bullet_list(self):
        return [b.strip("•- ").strip() for b in self.bullets.splitlines() if b.strip()]

    def get_rag_text(self):
        return f"Experience: {self.role} at {self.company}. {self.bullets}"

    def __str__(self):
        return f"{self.role} — {self.company}"


class Skill(OrderedModel):
    CATEGORY_CHOICES = [
        ("language", "Languages"),
        ("os", "Operating Systems"),
        ("networking", "Networking"),
        ("framework", "Frameworks & Tools"),
        ("cs", "Core CS"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="other", db_index=True)
    proficiency = models.IntegerField(default=3, help_text="1-5")

    def get_rag_text(self):
        return f"Skill: {self.name} ({self.get_category_display()}, level {self.proficiency}/5)"

    def __str__(self):
        return self.name


class Project(OrderedModel, TimeStampedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=300)
    description = models.TextField()
    technologies = models.ManyToManyField(Skill, blank=True, related_name="projects")
    github_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    cover_image = models.ImageField(upload_to="projects/", blank=True, null=True)
    featured = models.BooleanField(default=False, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project-detail", args=[self.slug])

    def get_rag_text(self):
        techs = ", ".join(t.name for t in self.technologies.all())
        return f"Project: {self.title}. {self.summary} {self.description} Technologies: {techs}"

    def __str__(self):
        return self.title


class BlogPost(TimeStampedModel):
    """Local post, optionally mirroring a LinkedIn post."""

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    body = models.TextField(help_text="Full text (paste your LinkedIn post here)")
    excerpt = models.TextField(blank=True, help_text="Auto-filled from body if empty; used for RAG + cards")
    linkedin_url = models.URLField(blank=True, null=True, unique=True)
    linkedin_embed_html = models.TextField(blank=True, help_text="Sanitized LinkedIn iframe. Auto-cleaned on save.")
    published_at = models.DateField(null=True, blank=True, db_index=True)
    is_published = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:50]
        if not self.excerpt:
            self.excerpt = self.body[:280]
        if self.linkedin_embed_html:
            self.linkedin_embed_html = bleach.clean(
                self.linkedin_embed_html,
                tags=["iframe"],
                attributes={"iframe": ["src", "height", "width", "frameborder", "allowfullscreen", "title"]},
                strip=True,
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog-detail", args=[self.slug])

    def get_rag_text(self):
        return f"Blog: {self.title}. {self.excerpt} {self.body[:1000]}"

    def __str__(self):
        return self.title


class ContactMessage(TimeStampedModel):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField(max_length=2000)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} <{self.email}>"
