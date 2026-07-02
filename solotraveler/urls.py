"""
URLs raiz do projeto Solo Traveler.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # rota para trocar de idioma (i18n) - usada pelo formulário no base.html
    path('i18n/', include('django.conf.urls.i18n')),

    # API REST (não precisa de prefixo de idioma)
    path('api/', include('travels.api_urls')),
]

# páginas HTML ficam com prefixo de idioma (/pt-br/... ou /en/...)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('travels.urls')),
    prefix_default_language=True,
)

# serve as fotos de capa enviadas pelos usuários durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
