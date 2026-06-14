from django.contrib import admin
from django.urls import path
from dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('telegram-auth/', views.telegram_auth, name='telegram_auth'),
    path('users/', views.users_list, name='users'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('korxonalar/', views.korxonalar_list, name='korxonalar'),
    path('korxonalar/add/', views.korxona_add, name='korxona_add'),
    path('korxonalar/<int:k_id>/edit/', views.korxona_edit, name='korxona_edit'),
    path('korxonalar/<int:k_id>/delete/', views.korxona_delete, name='korxona_delete'),
    path('bot/toggle/', views.bot_toggle, name='bot_toggle'),
    path('register/', views.register_view, name='register'),
]
