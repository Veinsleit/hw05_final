from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    if not request.user.is_authenticated:
        following = False
    else:
        following = Follow.objects.filter(
            author=user,
            user=request.user,
        ).exists()
    post_list = user.posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'profile_user': user,
        'post_count': post_count,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    post_count = post.author.posts.all().count()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_count': post_count,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/post_create.html'
    if request.method == 'POST':
        form = PostForm(
            request.POST,
            files=request.FILES or None
        )
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('posts:profile', request.user)
        else:
            return render(request, template, {'form': form})
    else:
        form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/post_create.html'
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    context = {'form': form, 'is_edit': is_edit}
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    else:
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        else:
            return render(request, template, context)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    else:
        post.delete()
        return render(request, 'posts/post_delete.html')


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', request.user)
    else:
        follow = Follow.objects.create(
            author=author,
            user=request.user,
        )
        follow.save()
        return redirect('posts:index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        author=author,
        user=request.user,
    )
    follow.delete()
    return redirect('posts:index')
