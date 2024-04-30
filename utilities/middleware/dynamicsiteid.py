from django.contrib.sites.models import Site
from django.conf import settings

class DynamicSiteIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Your middleware logic here
        try:
            current_site = Site.objects.get(domain=request.get_host())
            settings.SITE_ID = current_site.id
        except Site.DoesNotExist:
            # Fallback to a default site if the requested domain is not found
            settings.SITE_ID = 1
            current_site = Site.objects.get(id=settings.SITE_ID)

        # Attach the site object to the request
        request.current_site = current_site

        # Get the response from the next middleware or view
        response = self.get_response(request)

        # You can modify the response here if needed

        return response
