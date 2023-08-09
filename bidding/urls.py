from django.urls import path
from . import views
from .views import ItemDeleteView,signup,login_view,logout_view,ItemUpdateView,item_catagory,CategoryListView,search



urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('create/', views.item_create, name='item_create'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:pk>/delete',ItemDeleteView.as_view(), name='item_delete'),
    path('signup/',signup,name="signup"),
    path('login/',login_view,name="login"),
    path('logout/',logout_view,name="logout"),
    path('<int:pk>/update', ItemUpdateView.as_view(), name ='item_update'),
    path('categories/<int:id>', views.item_catagory, name='item_category'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path("search_results", views.search, name="results"),




]


