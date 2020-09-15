"""ra URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url

import rest_auth
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token
from .routers import router
from .settings.base import *
from ra_user import views
from players import views as player_view
from ra_scraping import views as ra_scraping_views
from address import views as address_view

urlpatterns = [
    url(r'^superadmin/', admin.site.urls),
    url(r'^api/', include(router.urls)),
    url(r'^$', RedirectView.as_view(url='/api/', permanent=False)),
    url(r'^', include('django.contrib.auth.urls')),
    # url for authentication
    url(r'^login/$', LoginView.as_view(
        redirect_authenticated_user=True,
        template_name='registration/login.html'),
        name='login'
        ),
    url(r'^logout/$', LogoutView.as_view(
        next_page=reverse_lazy('login')),
        name='logout'),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='ra_auth')),
    url(r'^api/auth/', include('rest_auth.urls')),
    url(r'^api/login/', views.CustomLoginView.as_view(), name="api/login"),
    url(r'^api/auth/forgot/password/', views.CustomPasswordResetView.as_view(),),
    url(r'^api/auth/verify-otp/', views.VerifyOtpView.as_view(),),
    url(r'^api/auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        TemplateView.as_view(), name='password_reset_confirm'),
    url(r'^api/password-change', views.CustomSetPasswordView.as_view()),
    url(r'^api/export_players', views.myboard_export_view,
        name='myboard_export_view'),
    url(r'^api/update_player', player_view.player_update_view,
        name='player_update_view'),
    url(r'^api/admin_export_players', player_view.admin_export_view,
        name='admin_export_view'),
    url(r'^api/admin_export_users',views.export_user_csv,
        name='export_user_csv'),
    url(r'^api/admin_export_college',address_view.export_college_csv,
        name='export_college_csv'),
    url(r'^api/admin_export_school',address_view.export_school_csv,
        name='export_school_csv'),
    url(r'^api/add_update_school', address_view.school_add_update_view,
        name='school_add_update_view'),
    url(r'^api/get_positions_list', player_view.get_position_list,
        name='get_position_list'),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
