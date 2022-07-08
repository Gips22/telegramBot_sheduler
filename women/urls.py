from django.urls import path, re_path

from .views import * # . означает что из папки women импортируем

urlpatterns = [
    path('home/', index, name='home'),
    path('cats/<int:catid>/', categories),   # маршрутизатор ожидает число для номера страницы cats
    re_path(r'^archive/(?P<year>[0-9]{4})/', archive),
]