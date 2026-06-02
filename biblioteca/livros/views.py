from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from .forms import BibliotecaAuthenticationForm, LivroForm
from .models import Livro
from .services import LivroService


class BibliotecaLoginView(LoginView):
    """Authenticate users with Django's native username/password flow."""

    template_name = 'livros/login.html'
    authentication_form = BibliotecaAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('livros:lista_livros')


class BibliotecaLogoutView(LogoutView):
    """End the current user session and return to the catalogue."""

    next_page = reverse_lazy('livros:lista_livros')


class LivroListMixin:
    """Shared query behavior for pages that list Livro cards."""

    model = Livro
    context_object_name = 'livros'

    def get_queryset(self):
        return LivroService.listar()


class HomeLivrosView(LivroListMixin, ListView):
    template_name = 'livros/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        return context


class ListaLivrosView(LivroListMixin, ListView):
    template_name = 'livros/livros.html'


class LivroDetailView(DetailView):
    model = Livro
    template_name = 'livros/livro_form.html'
    context_object_name = 'livro'
    slug_field = 'isbn'
    slug_url_kwarg = 'isbn'

    def get_object(self, queryset=None):
        return LivroService.obter_por_isbn(self.kwargs['isbn'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mode': 'detail',
            'page_title': 'Detalhes do livro',
            'submit_label': None,
        })
        return context


class LivroCreateView(CreateView):
    model = Livro
    form_class = LivroForm
    template_name = 'livros/livro_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mode': 'create',
            'page_title': 'Novo livro',
            'submit_label': 'Inserir',
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Livro inserido com sucesso.')
        return response

    def get_success_url(self):
        return reverse_lazy('livros:detalhe_livro', kwargs={'isbn': self.object.isbn})


class LivroUpdateView(UpdateView):
    model = Livro
    form_class = LivroForm
    template_name = 'livros/livro_form.html'
    context_object_name = 'livro'
    slug_field = 'isbn'
    slug_url_kwarg = 'isbn'

    def get_object(self, queryset=None):
        return LivroService.obter_por_isbn(self.kwargs['isbn'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['readonly_isbn'] = True
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'mode': 'edit',
            'page_title': 'Editar livro',
            'submit_label': 'Guardar alteracoes',
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Livro atualizado com sucesso.')
        return response

    def get_success_url(self):
        return reverse_lazy('livros:detalhe_livro', kwargs={'isbn': self.object.isbn})


class LivroDeleteView(View):
    template_name = 'livros/livro_confirm_delete.html'

    def get_livro(self):
        return LivroService.obter_por_isbn(self.kwargs['isbn'])

    def get(self, request, *args, **kwargs):
        livro = self.get_livro()
        return render(request, self.template_name, {'livro': livro})

    def post(self, request, *args, **kwargs):
        livro = self.get_livro()
        titulo = livro.titulo
        LivroService.apagar(livro)
        messages.success(request, f'Livro "{titulo}" apagado com sucesso.')
        return redirect('livros:lista_livros')


def page_not_found(request, exception):
    """Render project 404 errors inside the normal site layout."""

    message = str(exception) if exception else 'Pagina nao encontrada.'
    return render(request, 'livros/404.html', {'message': message}, status=404)
