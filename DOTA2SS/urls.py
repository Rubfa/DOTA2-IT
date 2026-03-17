from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('', include('visualisation.urls')),
    path('items/', include('visualisation.urls')),
    
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('admin/', admin.site.urls),

    path('messageboard/', include('messageboard.urls')),
    path('mocktrade/', include('mocktrade.urls')),
    path('visualisation/', include('visualisation.urls')),

    path('test/', views.home_test, name='home_test')
]
