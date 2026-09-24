from django.db import models


class BannerContent(models.Model):

    BANNER_TYPE_CHOICES = (
        ("container", "Container"),
        ("inquiry", "Inquiry"),
        ("marketing_popup", "Marketing Popup"),
    )

    LANGUAGE_CHOICES = (
        ("en", "English"),
        ("fr", "French"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
    )

    banner_type = models.CharField(max_length=50,choices=BANNER_TYPE_CHOICES)
    language = models.CharField(max_length=10,choices=LANGUAGE_CHOICES,default="en")
    title = models.CharField(max_length=255,blank=True,null=True)
    image = models.ImageField(upload_to="banner/",blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["banner_type", "language"],
                name="unique_banner_type_language"
            )
        ]

    def __str__(self):
        return f"{self.banner_type} - {self.language}"