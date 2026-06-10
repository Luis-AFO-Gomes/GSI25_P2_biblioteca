# Authentication workflow

This document explains how authentication and authorization work in this Django project, and which files participate in each step.

## 1. Django is enabled as the authentication provider

The project uses Django's built-in authentication system instead of a custom user model.

- `biblioteca/biblioteca/settings.py` includes `django.contrib.auth`, which provides the `User`, `Group`, permission models, password hashing, and authentication backends used by Django.
- The same settings file includes `django.contrib.sessions`, which stores the logged-in user's session, and `django.contrib.messages`, which is used for success messages after book CRUD actions.
- `SessionMiddleware` must run before `AuthenticationMiddleware`, because authentication reads the user id from the session. In this project the middleware order is correct: session middleware is listed before authentication middleware.
- `AuthenticationMiddleware` attaches `request.user` to every request. That is the object used throughout the views and templates to decide whether the visitor is anonymous, authenticated, or belongs to a group.
- The template context processors include `django.template.context_processors.request` and `django.contrib.auth.context_processors.auth`, which makes `request` and `user`-related authentication data available in templates.
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL` define the default authentication URLs and fallback redirects for Django authentication views.

Relevant file: `biblioteca/biblioteca/settings.py`.

## 2. URL routing sends login/logout requests to the app views

The project URL configuration includes `livros.urls` at the site root, so `/login/`, `/logout/`, `/catalogo/`, and the book routes are resolved from the `livros` app.

The app URL configuration maps:

- `/login/` to `BibliotecaLoginView`.
- `/logout/` to `BibliotecaLogoutView`.
- `/registo-socio/` to `SubscriptionView`.
- `/catalogo/` to `ListaLivrosView`.
- `/livro/novo/`, `/livro/<isbn>/editar/`, and `/livro/<isbn>/apagar/` to the protected book management views.
- `/livro/<isbn>/` to the protected book detail view.

Relevant files:

- `biblioteca/biblioteca/urls.py`
- `biblioteca/livros/urls.py`

## 3. The login form references Django's native AuthenticationForm

`BibliotecaAuthenticationForm` is a small customization of Django's `AuthenticationForm`.

It does not implement its own password check. Instead, it inherits Django's normal username/password validation workflow and only changes labels/placeholders to Portuguese:

1. The browser posts `username`, `password`, and the CSRF token to `/login/`.
2. `BibliotecaLoginView`, because it inherits from Django's `LoginView`, instantiates `BibliotecaAuthenticationForm`.
3. Django's inherited `AuthenticationForm` validates the credentials using Django authentication internals.
4. If the credentials are invalid, non-field errors are sent back to the login template.
5. If the credentials are valid, Django's `LoginView` logs the user in by writing authentication data into the session.

Relevant files:

- `biblioteca/livros/forms.py`
- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/login.html`

## 4. The login view delegates most work to Django's LoginView

`BibliotecaLoginView` inherits from `django.contrib.auth.views.LoginView`.

The project-specific configuration is:

- `template_name = 'livros/login.html'`: use this project's login template.
- `authentication_form = BibliotecaAuthenticationForm`: use the customized Portuguese form.
- `redirect_authenticated_user = True`: if an already-authenticated user opens `/login/`, Django redirects them instead of showing the login page again.
- `get_success_url()` returns the named catalogue URL, so a successful login goes to the catalogue.

The actual session creation is handled by Django's parent `LoginView`, not by custom code in this project.

Relevant file: `biblioteca/livros/views.py`.

## 5. The login template posts credentials safely

The login page contains a normal POST form that sends credentials to the login route.

Important details:

- `{% csrf_token %}` protects the POST against CSRF attacks.
- The template renders form-level errors and field-level errors.
- If Django provides a `next` value, the template preserves it in a hidden field. In the current project, successful login is explicitly redirected to the catalogue by `BibliotecaLoginView.get_success_url()`.

Relevant file: `biblioteca/livros/templates/livros/login.html`.

## 6. After login, request.user drives the UI

Once a user is logged in, Django's session and authentication middleware populate `request.user` on later requests.

The base template uses that value to decide what to show in the header:

- Anonymous users see a `Login` link.
- Authenticated users see a menu with their full name, falling back to username.
- The menu shows the first group name if the user has a group; otherwise it displays `membro` as the default profile label.
- Logout is a POST form, also protected with `{% csrf_token %}`.

Relevant file: `biblioteca/livros/templates/livros/master.html`.

## 7. Logout delegates to Django's LogoutView

`BibliotecaLogoutView` inherits from Django's `LogoutView`.

The app only sets `next_page` to the catalogue route. Django's parent logout view clears the authentication session data, so future requests become anonymous again.

Relevant files:

- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/master.html`

## 8. Authorization is implemented with helper functions, not Django decorators

This project does not use `@login_required`, `LoginRequiredMixin`, `PermissionRequiredMixin`, or model-level Django permissions for the book pages.

Instead, it centralizes the rules in two helper functions:

- `can_view_book_detail(user)` returns `True` when `user.is_authenticated` is true.
- `can_manage_books(user)` first rejects anonymous users, then checks whether the user belongs to either the `socio` or `administrador` group.

The group names that grant management access are stored in `MANAGER_GROUPS = {'socio', 'administrador'}`.

Relevant file: `biblioteca/livros/views.py`.

## 9. Catalogue behavior changes based on authentication and group membership

`ListaLivrosView` adds two permission flags to the template context:

- `can_view_book_detail`
- `can_manage_books`

The catalogue template uses those flags as follows:

- If `can_manage_books` is true, show the `Novo livro` button.
- Else, if the visitor is anonymous, show the `Registo Sócio` button.
- The book grid receives `can_view_book_detail`; authenticated users get clickable book cards and status information, while anonymous visitors get static cards without status.

Relevant files:

- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/livros.html`
- `biblioteca/livros/templates/livros/_book_grid.html`

## 10. Book detail is protected by dispatch()

`LivroDetailView` overrides `dispatch()`.

Every request to the detail page passes through `dispatch()` before Django runs the normal detail-view logic. The view checks `can_view_book_detail(request.user)`:

- Anonymous users are redirected to the catalogue.
- Authenticated users continue to the normal detail view.

Inside the detail page, the context also includes `can_manage_books`. The template uses that flag to show or hide the `Editar` and `Apagar` actions.

Relevant files:

- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/livro_form.html`

## 11. Create, update, and delete are protected by group membership

The create, update, and delete views each override `dispatch()` and check `can_manage_books(request.user)` before doing any work.

- `LivroCreateView`: anonymous users, users without a group, and users in `membro` are redirected to the catalogue.
- `LivroUpdateView`: unauthorized users are redirected back to the book detail page.
- `LivroDeleteView`: unauthorized users are redirected back to the book detail page.

Only users in `socio` or `administrador` are allowed to create, edit, or delete books.

Relevant file: `biblioteca/livros/views.py`.

## 12. Registration/subscription validates data but does not create users

The public `Registo Sócio` flow is not the same thing as creating a Django account.

`SubscriptionForm` imports Django's `User` model and `validate_password`, but it only validates the request:

- `clean_username()` rejects usernames that already exist in Django's user table.
- `clean()` checks whether password and confirmation match.
- `clean()` also calls Django's `validate_password(password, user=user)`, so the configured password validators in `settings.py` are applied.

`SubscriptionView.post()` then displays the submitted identity data and the notice that the functionality is not implemented and the user was not added. It does not call `User.objects.create_user()`.

Relevant files:

- `biblioteca/livros/forms.py`
- `biblioteca/livros/views.py`
- `biblioteca/livros/templates/livros/subscription.html`

## 13. Tests describe the expected authentication behavior

The tests document and verify the current behavior:

- Login page renders Portuguese username/password labels.
- Valid login redirects to the catalogue.
- Anonymous users see a login button.
- Authenticated users see username/profile/logout in the header.
- Logout removes `_auth_user_id` from the session.
- Guests cannot open book details.
- Authenticated users without a management group can view details but cannot manage books.
- `membro` users can view details but cannot manage books.
- `socio` and `administrador` users can manage books.
- A user with multiple groups gets the highest permission because membership in `socio` is enough to pass `can_manage_books()`.
- Subscription validates duplicate usernames, password mismatch, and Django password validators without creating a user.

Relevant file: `biblioteca/livros/tests.py`.

## End-to-end request flow examples

### Successful login

1. User opens `/login/`.
2. `biblioteca/biblioteca/urls.py` includes `livros.urls`.
3. `biblioteca/livros/urls.py` routes `login/` to `BibliotecaLoginView`.
4. `BibliotecaLoginView` renders `livros/login.html` with `BibliotecaAuthenticationForm`.
5. User submits username/password.
6. Django's inherited `AuthenticationForm` validates credentials using the built-in auth system.
7. Django's inherited `LoginView` stores the authenticated user id in the session.
8. `get_success_url()` redirects to the catalogue.
9. Later requests have `request.user.is_authenticated == True` because session and authentication middleware rebuild the user from the session.
10. `master.html`, `livros.html`, `_book_grid.html`, and `livro_form.html` change what they render based on `request.user` and the permission flags from the views.

### Guest opening a book detail URL

1. Guest opens `/livro/<isbn>/`.
2. The URL routes to `LivroDetailView`.
3. `dispatch()` calls `can_view_book_detail(request.user)`.
4. For an anonymous user, `user.is_authenticated` is false.
5. The view redirects to the catalogue instead of showing the detail page.

### `socio` creating a book

1. Authenticated user opens `/livro/novo/`.
2. The URL routes to `LivroCreateView`.
3. `dispatch()` calls `can_manage_books(request.user)`.
4. The helper checks `request.user.groups.filter(name__in={'socio', 'administrador'}).exists()`.
5. If the user belongs to `socio`, the request continues to Django's `CreateView` workflow.
6. On valid form submission, `form_valid()` saves the book, adds a success message, and redirects to the new book detail page.
