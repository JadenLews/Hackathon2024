from django.shortcuts import render, redirect, get_object_or_404
from .models import ProjectPost
from .forms import UserUpdateForm, ProfileUpdateForm, ProjectPostForm
from django.contrib.auth.decorators import login_required
from .models import Profile, ProjectPost
from .models import Profile
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.contrib.auth import get_user_model
from .managers import CustomUserManager
import random
from django.db.models import Avg
from django.http import HttpResponseNotFound
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q


def login(request):
    return render(request, "main/login.html")

def signup(request):
    return render(request, "main/signup.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get(
            "username"
        )  # Assuming your login form has a field named 'username'
        password = request.POST.get(
            "password"
        )  # Assuming your login form has a field named 'password'

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            # User is authenticated, log them in
            auth_login(request, user)
            return redirect("home")  # Redirect to home page after successful login
        else:
            # Authentication failed
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, "main/login.html")

def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        if not email.endswith("@clarku.edu"):
            messages.error(request, "Must use a Clark email address.")
            return redirect("signup")

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            messages.error(
                request, "Username already exists. Please choose a different username."
            )
            return redirect("signup")
        if User.objects.filter(email=email).exists():
            messages.error(
                request, "Email already exists. Please use a different email address."
            )
            return redirect("signup")

        user_manager = CustomUserManager()
        new_user = user_manager.create_user(
            username=username, email=email, password=password
        )

        return redirect("login")

    return render(request, "main/signup.html")
# Create your views here.
@login_required(login_url='/main/templates/main/login.html')
def portfolio_page(request):
    # Ensure the user has a profile
    if not hasattr(request.user, 'profile'):
        Profile.objects.create(user=request.user)

    # Fetch the user's posts if applicable
    user_posts = ProjectPost.objects.filter(user=request.user)

    context = {
        'user': request.user,
        'profile': request.user.profile,
        'posts': user_posts,
    }

    return render(request, "main/portfolio.html", context)


from django.shortcuts import render
from .models import ProjectPost, Profile

from .models import Notifications

def home(request):
    # Fetch all posts with related user profiles
    posts = ProjectPost.objects.all()
    
    # Create a list of posts with corresponding user profiles
    posts_with_profiles = []
    for post in posts:
        try:
            profile = Profile.objects.get(user=post.user)  # Get profile for each post's user
        except Profile.DoesNotExist:
            profile = None  # In case the user has no profile

        posts_with_profiles.append({
            'post': post,
            'profile_image': profile.profile_image.url if profile and profile.profile_image else None
        })

    # Fetch notifications for the logged-in user (if logged in)
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)  # Get the current user's profile
        # Filter out notifications with 'accepted' status and only get pending or rejected
        notifications = Notifications.objects.filter(post_owner=user_profile).exclude(status='accepted')  
    else:
        notifications = []  # No notifications if the user is not logged in

    context = {
        'posts': posts_with_profiles,
        'notifications': notifications,  # Pass the filtered notifications to the template
    }

    return render(request, "main/home.html", context)




@login_required(login_url='/main/templates/main/login.html')
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('/portfolio2')  # Redirect to portfolio page after saving
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'profile.html', context)

@login_required
def save_social_links(request):
    profile = request.user.profile  # Assuming a OneToOne relationship between User and Profile

    if request.method == 'POST':
        # Get data from the form
        profile.linkedin = request.POST.get('linkedin', '')
        profile.git = request.POST.get('github', '')
        profile.choice_site = request.POST.get('twitter', '')

        # Save the updated profile data
        profile.save()

        return redirect('profile')  # Redirect to the profile page

    return render(request, 'portfolio.html', {'profile': profile})

@login_required(login_url='/main/templates/main/login.html')
def create_project_post(request):
    if request.method == 'POST':
        form = ProjectPostForm(request.POST)
        if form.is_valid():
            project_post = form.save(commit=False)
            project_post.user = request.user
            project_post.save()  # Saving the project post with all fields
            messages.success(request, 'Project created successfully!')
            return redirect('home')
        else:
            messages.error(request, 'There was an error with your form. Please check the details.')
    else:
        form = ProjectPostForm()

    return render(request, 'main/create_project_post.html', {'form': form})

def portfolio_page2(request, username):
    # Fetch the user by the username from the URL, or return a 404 if not found
    User = get_user_model()
    user = get_object_or_404(User, username=username)

    # Ensure the user has a profile
    if not hasattr(user, 'profile'):
        Profile.objects.create(user=user)

    # Fetch the user's posts
    user_posts = ProjectPost.objects.filter(user=user)

    context = {
        'user': user,
        'profile': user.profile,
        'posts': user_posts,
    }

    return render(request, "main/portfolio.html", context)


def search(request):
    query = request.GET.get("q")
    
    # Filter posts based on the search query
    results = ProjectPost.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(description_long__icontains=query) | Q(categories__icontains=query) | Q(skills__icontains=query))
    
    # Prepare the results with the associated profiles
    results_with_profiles = []
    for post in results:
        try:
            profile = Profile.objects.get(user=post.user)  # Get profile for each post's user
        except Profile.DoesNotExist:
            profile = None  # In case the user has no profile

        results_with_profiles.append({
            'post': post,
            'profile_image': profile.profile_image.url if profile and profile.profile_image else None
        })
    


    # Fetch notifications for the logged-in user (if logged in)
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user)  # Get the current user's profile
        # Filter out notifications with 'accepted' status and only get pending or rejected
        notifications = Notifications.objects.filter(post_owner=user_profile).exclude(status='accepted')  
    else:
        notifications = []  # No notifications if the user is not logged in




    context = {
        'results': results_with_profiles,
        'query': query,
        'notifications': notifications, 
    }
    
    return render(request, "main/search_results.html", context)

def search_results(request):
    return render(request, "main/search_results.html")

@login_required(login_url='/main/templates/main/login.html')
def request_to_join(request, post_id):
    # Get the post and its owner
    post = get_object_or_404(ProjectPost, id=post_id)
    post_owner = get_object_or_404(Profile, user=post.user)
    
    # Get the requestor (logged-in user's profile)
    requestor = get_object_or_404(Profile, user=request.user)
    
    # Create the notification
    notification = Notifications.objects.create(
        requestor=requestor,
        post_owner=post_owner,
        post=post,
        status='pending'
    )
    
    # Redirect back to the home page or a success page
    return redirect('home')


@login_required
def accept_request(request, notification_id):
    # Get the notification object
    notification = get_object_or_404(Notifications, id=notification_id)
    
    # Ensure the current user is the post owner
    if notification.post_owner.user == request.user:
        notification.status = 'accepted'
        notification.save()

    return redirect('home')  # Redirect back to home or wherever you want

@login_required
def reject_request(request, notification_id):
    # Get the notification object
    notification = get_object_or_404(Notifications, id=notification_id)

    # Ensure the current user is the post owner
    if notification.post_owner.user == request.user:
        notification.delete()  # Delete the notification object

    return redirect('home')