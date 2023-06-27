from typing import Any, Dict

from blog.models import Post, Category, Comment
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, DetailView
)
from django.contrib.auth import get_user_model
from .forms import PostForm, CommentForm, ChangeUserForm
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

dnow = timezone.now()
User = get_user_model()


class IndexListView(LoginRequiredMixin, ListView):
    template_name = 'blog/index.html'
    model = Post
    queryset = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=dnow
    ).select_related('location', 'author', 'category')
    ordering = '-pub_date'
    paginate_by = 10


def category_posts(request, category_slug):
    '''Отображение постов в данной категории'''
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.values(
            'title',
            'description'
        ),
        slug=category_slug,
        is_published=True
    )
    post_list = Post.objects.only(
        'title',
        'pub_date',
        'text',
        'id',
        'location',
        'author__username'
    ).filter(
        is_published=True,
        pub_date__lte=dnow,
        category__slug=category_slug
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'category': category,
    }
    return render(request, template, context)


class ProfileListView(ListView, LoginRequiredMixin):
    '''Страница пользователя'''
    template_name = 'blog/profile.html'
    model = User
    paginate_by = 10
    ordering = '-pub_date'
    context_object_name = 'page_obj'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context

    def get_queryset(self):
        self.author = get_object_or_404(
            User, username=self.kwargs['username']
        )
        return Post.objects.select_related(
            'location',
            'author',
            'category',
        ).filter(author=self.author,)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    '''Сраница редактирования профиля'''
    template_name = 'blog/user.html'
    model = User
    form_class = ChangeUserForm
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def form_valid(self, form):
        form.instance.username = self.kwargs['username']
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.kwargs['username']
        return context

    def dispatch(self, request, *args, **kwargs):
        profile = get_object_or_404(User, username=self.kwargs['username'])
        if profile != self.request.user:
            return redirect('blog:profile', self.kwargs['username'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    '''Страница создания поста'''
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    '''Страница редактирования поста'''
    template_name = 'blog/create.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'pk'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.kwargs['pk']
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author != self.request.user:
            return redirect('blog:post_detail', post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    '''Страница удаления поста'''
    template_name = 'blog/create.html'
    model = Post
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if post.author != self.request.user:
            return redirect('blog:post_detail', post.pk)
        return super().dispatch(request, *args, **kwargs)


class PostDetailView(LoginRequiredMixin, DetailView):
    '''Отображение деталий поста'''
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/comment.html'
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        if comment.author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    '''Страница удаления поста'''
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        if comment.author != self.request.user:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs['post_id']})
