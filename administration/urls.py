from django.urls import path
from . import views

urlpatterns= [
    path("administration/", views.administration_site, name="administration-site"),
    path("administration/users", views.users, name="users"),
    path("administration/messages", views.messages, name="messages"),
    path("administration/exceptions", views.exceptions, name="exceptions"),
    path("administration/excercises", views.excercises, name="excercises"),
    path("administration/admins", views.admins, name="admins"),
    path("administration/excercises/add", views.add_excercise, name="add-excercise"),
    path("administration/messages/<mid>", views.message, name="message"),
    path("administration/exception/<eid>", views.exception, name="exception"),
    path("administration/messages/<mid>/delete", views.delete_message, name="delete-message"),

]
