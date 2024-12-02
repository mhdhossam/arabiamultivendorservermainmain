from django.template.defaultfilters import slugify


def create_slug(key):
    slug = slugify(key)

    return slug
