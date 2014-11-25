from django.conf import settings


def tracking_code(request):
    return {"PRIVATE_GOOGLE_ANALYTICS_KEY":
                settings.PRIVATE_GOOGLE_ANALYTICS_KEY,
            "EUSA_GOOGLE_ANALYTICS_KEY":
                settings.EUSA_GOOGLE_ANALYTICS_KEY}