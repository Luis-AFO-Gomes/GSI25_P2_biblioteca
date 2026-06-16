from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from .forms import ArvoreForm
from .models import Arvore
from .services import ArvoreService

class ArvoreListMixin:

    model = Arvore
    context_object_name = 'arvores'

    def get_queryset(self):
        return ArvoreService.listar()

class HomeArvoresView(ArvoreListMixin, ListView):

    template_name = 'livros/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Venus07'
        return context

class ListaArvoresView(ArvoreListMixin, ListView):

    template_name = 'livros/arvores.html'

class ArvoreDetailView(DetailView):

    model = Arvore
    template_name = 'livros/arvore_form.html'
    context_object_name = 'arvore'

    def get_object(self, queryset=None):
        return ArvoreService.obter_por_id(
            self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({
            'mode': 'detail',
            'page_title': 'Detalhes da árvore',
            'submit_label': None,
        })

        return context


class ArvoreCreateView(CreateView):

    model = Arvore
    form_class = ArvoreForm

    template_name = 'livros/arvore_form.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({
            'mode': 'create',
            'page_title': 'Nova árvore',
            'submit_label': 'Inserir',
        })

        return context

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            'Árvore inserida com sucesso.'
        )

        return response

    def get_success_url(self):

        return reverse_lazy(
            'livros:detalhe_arvore',
            kwargs={'pk': self.object.id}
        )


class ArvoreUpdateView(UpdateView):

    model = Arvore
    form_class = ArvoreForm

    template_name = 'livros/arvore_form.html'

    context_object_name = 'arvore'

    def get_object(self, queryset=None):

        return ArvoreService.obter_por_id(
            self.kwargs['pk']
        )

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({
            'mode': 'edit',
            'page_title': 'Editar árvore',
            'submit_label': 'Guardar alterações',
        })

        return context

    def get_success_url(self):

        return reverse_lazy(
            'livros:detalhe_arvore',
            kwargs={'pk': self.object.id}
        )


class ArvoreDeleteView(View):

    template_name = 'livros/arvore_confirm_delete.html'

    def get_arvore(self):

        return ArvoreService.obter_por_id(
            self.kwargs['pk']
        )

    def get(self, request, *args, **kwargs):

        arvore = self.get_arvore()

        return render(
            request,
            self.template_name,
            {'arvore': arvore}
        )

    def post(self, request, *args, **kwargs):

        arvore = self.get_arvore()

        nome = arvore.nome

        ArvoreService.apagar(arvore)

        messages.success(
            request,
            f'Árvore "{nome}" apagada com sucesso.'
        )

        return redirect('livros:lista_arvores')
    message = str(exception) if exception else 'Pagina nao encontrada.'
    return render(request, 'livros/404.html', {'message': message}, status=404)
