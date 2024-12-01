from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.index, name='index'),
    path('postbook', views.postbook, name='postbook'),
    path('displaybooks', views.displaybooks, name='displaybooks'),
    path('mybooks', views.mybooks, name='mybooks'),
    path('book_detail/<int:book_id>', views.book_detail, name='book_detail'),
    path('book_delete/<int:book_id>', views.book_delete, name='book_delete'),
    path('search', views.search_books, name='search_books'),
    path('rate_book/<int:book_id>/', views.rate_book, name='rate_book'),
    path('aboutus', views.about, name='about'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('add_to_favorites/<int:book_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:book_id>/', views.remove_from_favorites, name='remove_from_favorites'),
]


