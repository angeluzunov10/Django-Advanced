from datetime import datetime

from django.forms import modelform_factory
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, RedirectView, ListView, FormView, CreateView, DeleteView, UpdateView, \
    DetailView

from forumApp.decorators import measure_execution_time
from forumApp.posts.forms import PostCreateForm, PostDeleteForm, SearchForm, CommentFormSet
from forumApp.posts.models import Post


# Create your views here.

@method_decorator(measure_execution_time, name='dispatch')
class IndexView(TemplateView):
    template_name = 'common/index.html'  # static way
    extra_context = {
        'static_time': datetime.now(),
    }  # static way

    def get_context_data(self, **kwargs):  # dynamic way
        context = super().get_context_data(**kwargs)

        context['dynamic_time'] = datetime.now()

        return context

    def get_template_names(self):  # dynamic way
        if self.request.user.is_authenticated:
            return ['common/index_logged_in.html']              # dynamic way for template
        else:
            return ['common/index.html']


# def index(request):
#
#     context = {
#         "my_form": '',
#     }
#
#     return render(request, 'common/index.html', context=context)


class DashboardView(ListView, FormView):
    template_name = 'posts/dashboard.html'
    context_object_name = 'posts'
    form_class = SearchForm
    paginate_by = 6
    success_url = reverse_lazy('dash')

    model = Post

    def get_queryset(self):
        queryset = self.model.objects.all()

        if 'query' in self.request.GET:
            query = self.request.GET.get('query')

            queryset = self.queryset.filter(title__icontains=query)

        return queryset

# def dashboard(request):
#     form = SearchForm(request.GET)
#     posts = Post.objects.all()
#
#     if request.method == 'GET':
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             posts = posts.filter(title__icontains=query)
#
#     context = {
#         "posts": posts,
#         "form": form,
#     }
#
#     return render(request, 'posts/dashboard.html', context)


class AddPostView(CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'posts/add-post.html'
    success_url = reverse_lazy('dash')

# def add_post(request):
#     form = PostCreateForm(request.POST or None, request.FILES or None)
#
#     if request.method == 'POST':
#         if form.is_valid():
#             form.save()
#             return redirect('dash')
#
#     context = {
#         'form': form,
#     }
#
#     return render(request, 'posts/add-post.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/details-post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = CommentFormSet
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()

        formset = CommentFormSet(request.POST or None)

        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    comment = form.save(commit=False)
                    comment.post = post
                    comment.save()

            return redirect('details-post', pk=post.id)

        context = self.get_context_data()
        context['formset'] = formset

        return self.render_to_response(context)

# def details_post(request, pk):
#     post = Post.objects.get(pk=pk)
#     formset = CommentFormSet(request.POST or None)
#
#     if request.method == 'POST':
#         if formset.is_valid():
#             for form in formset:
#                 if form.cleaned_data:
#                     comment = form.save(commit=False)
#                     comment.post = post
#                     comment.save()
#
#             return redirect('details-post', pk=post.id)
#
#     context = {
#         'post': post,
#         'formset': formset,
#     }
#
#     return render(request, 'posts/details-post.html', context)


class EditPostView(UpdateView):
    model = Post
    template_name = 'posts/edit-post.html'
    success_url = reverse_lazy('dash')

    def get_form_class(self):
        if self.request.user.is_superuser:
            return modelform_factory(Post, fields=('title', 'content', 'author', 'languages'))
        else:
            return modelform_factory(Post, fields=('content',))


# def edit_post(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     if request.method == 'POST':
#         form = PostEditForm(request.POST, instance=post)
#
#         if form.is_valid():
#             form.save()
#             return redirect('dash')
#
#     else:
#         form = PostEditForm(instance=post)
#
#     context = {
#         'post': post,
#         'form': form,
#     }
#
#     return render(request, 'posts/edit-post.html', context)

class DeletePostView(DeleteView, FormView):
    model = Post
    form_class = PostDeleteForm
    template_name = 'posts/delete-post.html'
    success_url = reverse_lazy('dash')

    def get_initial(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        post = Post.objects.get(pk=pk)
        return post.__dict__


# def delete_post(request, pk):
#     post = Post.objects.get(pk=pk)
#     form = PostDeleteForm(instance=post)
#
#     if request.method == 'POST':
#         post.delete()
#         return redirect('dash')
#
#     context = {
#         'post': post,
#         'form': form,
#     }
#
#     return render(request, 'posts/delete-post.html', context)


class RedirectHomeView(RedirectView):
    url = reverse_lazy('index')