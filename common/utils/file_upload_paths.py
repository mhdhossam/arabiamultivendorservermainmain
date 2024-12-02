import os


def buyers_profile_pictures_path(instance, filename):
    return os.path.join(
        "users",
        "buyers",
        "profile_pictures",
        f"{instance.user.full_name}",
        filename,
    )


def suppliers_profile_pictures_path(instance, filename):
    return os.path.join(
        "users",
        "suppliers",
        "profile_pictures",
        f"{instance.user.full_name}",
        filename
    )


def suppliers_documents_path(instance, filename):
    return os.path.join(
        "users",
        "suppliers",
        "documents",
        f"{instance.user.full_name}",
        filename
    )


def categories_images_path(instance, filename):
    return os.path.join(
        "categories",
        "images",
        f"{instance.name}",
        filename,
    )


def brands_images_path(instance, filename):
    return os.path.join(
        "brands",
        "images",
        f"{instance.name}" ,
        filename,
    )
def ads_images_path(instance, filename):
    return os.path.join(
        "ads",
        "images",
        filename,
    )

def payment_screenshoot_path(instance,filename):
    return os.path.join(
        "payment",
        "images",
        filename
    )
def product_images_path(instance, filename):
    return os.path.join(
        "product",
        "images",
        "%s" % instance.product.name,
        filename,
    )


def quote_files_path(instance, filename):
    return os.path.join(
        "quote",
        "files",
        "%s" % instance.quote.user.id,
        filename,
    )


def return_request_files_path(instance, filename):
    return os.path.join(
        "return",
        "files",
        "%s" % instance.return_request.user.id,
        filename,
    )


def ads_thumbnail_images_path(instance, filename):
    return os.path.join(
        "advertisements",
        "files",
        filename,
    )


def company_profile_picture_path(instance, filename):
    return os.path.join(
        "company",
        instance.name,
        "profile_pictures",
        filename,
    )


def company_cover_picture_path(instance, filename):
    return os.path.join(
        "company",
        instance.name,
        "cover_pictures",
        filename,
    )


def withdraw_approve_receipt_path(instance, filename):
    return os.path.join(
        "transaction",
        "withdraw",
        instance.user.full_name,
        "receipts",
        filename,
    )
