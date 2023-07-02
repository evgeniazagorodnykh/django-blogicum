from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from blog.models import Post, Comment


class PostMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs.get('pk'))
        if post.author != self.request.user:
            return redirect('blog:post_detail', post.pk)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    template_name = 'blog/comment.html'
    model = Comment
    pk_url_kwarg = 'pk'

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=self.kwargs.get('pk'))
        if comment.author != self.request.user:
            return redirect('blog:post_detail', self.kwargs.get('post_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'pk': self.kwargs.get('post_id')})
