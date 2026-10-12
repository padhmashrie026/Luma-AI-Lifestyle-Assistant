"""URL configuration for the backend."""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.body_shape.urls")),
    path("api/wardrobe/", include("apps.wardrobe.urls")),
    path("api/outfits/", include("apps.outfits.urls")),
    path("api/diet/", include("apps.diet.urls")),
    path("api/expenses/", include("apps.expenses.urls")),
    path("api/lifestyle/", include("apps.lifestyle.urls")),
    path("api/tracking/", include("apps.tracking.urls")),
    path("api/insights/", include("apps.insights.urls")),
    # The build places the React index in templates/ and its assets in static_src/.
    # Keep this last and exclude backend/static paths from the SPA fallback.
    re_path(
        r"^(?!api(?:/|$)|admin(?:/|$)|static(?:/|$)).*$",
        TemplateView.as_view(template_name="index.html"),
        name="react-app",
    ),
]
