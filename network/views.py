import json

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import ModelForm, TextInput
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import User, Post


class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {'content': _('')}
        error_messages = {
            'content': {
                'max_length': _("This post is too long!"),
            },
        }
        widgets = {'content': TextInput(
            attrs={'placeholder': "What's happening?",
                   'class': "form-control"})}


def index(request, post_id=None, following=False):

    new_post = NewPostForm()
    user = request.user
    title = "All Posts"

    # Following page
    if bool(following) == True:
        if user.is_authenticated:
            followed_users = user.following.all()
            posts = Post.objects.filter(
                author__in=followed_users).order_by("-date")
            title = "Following"
        else:
            return HttpResponseRedirect(reverse("login"))
    else:
        posts = Post.objects.all().order_by("-date")

    # Pagination
    paginator = Paginator(posts, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":

        posted = NewPostForm(request.POST)

        # New Post
        if posted.is_valid():
            content = posted.cleaned_data['content']
            post = Post.objects.create(author=user, content=content)
            post.save()
            return HttpResponseRedirect(reverse("index"))

    # Like or edit Post
    if request.method == "PUT":
        data = json.loads(request.body)

        # Check if a post id is present
        if data.get("id") is not None:
            update_post = Post.objects.get(pk=data["id"])
        else:
            return JsonResponse({"message": "Invalid: id property not found"}, status=400)

        # If like data is present, check if already liked and change to the opposite
        if data.get("liked") is not None:
            if user in update_post.likes.all():
                liked = False
                update_post.likes.remove(user)
            else:
                liked = True
                update_post.likes.add(user)
            return JsonResponse({"like": liked, "message": "success"}, status=202)

        # Otherwise check if editing is present to update post
        elif data.get("new_content") is not None:
            # Check if current user wrote the post
            if user == update_post.author:
                # Check content exists
                if data.get("new_content") is not None:
                    update_post.content = data["new_content"]
                    update_post.save()
                    return JsonResponse({"update_post": update_post.content, "message": "success"}, status=202)
                else:
                    return JsonResponse({"error": "New content not found, cannot update post"}, status=400)
            else:
                return JsonResponse({"error": "Incorrect User, cannot update post"}, status=403)

    return render(request, "network/index.html", {"title": title, "new_post": new_post, "posts": page_obj})

# PROFILE PAGE


def profile(request, user=False, follow=None):
    # Get data for user profile page (own or someone elses)
    if user == False:
        user = request.user
    else:
        user = get_object_or_404(User, username=user)

    # follows
    total_following = user.total_following()
    followers = User.objects.filter(following=user)
    total_followers = followers.count()

    # check if user is viewing own page or someone elses
    own_profile = False
    already_following = False
    if user == request.user:
        own_profile = True
    # check if user already following. if not following then produce follow button in template
    elif request.user in followers:
        already_following = True

    # posts
    posts = Post.objects.filter(author__exact=user)
    ordered_posts = posts.order_by("-date")

    # follow button
    if request.method == "POST":
        if follow is not None:
            next = request.POST.get('next', '/')

            # Depending on what button shown on the page, follow or unfollow
            if follow == "True":
                request.user.following.add(user)
                return HttpResponseRedirect(next)

            elif follow == "False":
                request.user.following.remove(user)
                return HttpResponseRedirect(next)

    return render(request, "network/profile.html", {"title": user.username, "user": user, "total_following": total_following, "total_followers": total_followers, "followers": followers, "posts": ordered_posts, "own_profile": own_profile, "already_following": already_following})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
