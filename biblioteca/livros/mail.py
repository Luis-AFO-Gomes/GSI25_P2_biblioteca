from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


SUBSCRIPTION_CONFIRMATION_MESSAGE = (
    'O seu pedido de registo de sócio foi criado e aguarda validação por gestor da biblioteca'
)


def send_subscription_confirmation_email(subscription_data):
    """Send the subscription confirmation message to the requested email address."""

    html_body = render_to_string(
        'livros/emails/subscription_confirmation.html',
        {
            'message': SUBSCRIPTION_CONFIRMATION_MESSAGE,
            'subscription_data': subscription_data,
        },
    )
    email = EmailMultiAlternatives(
        subject='Pedido de registo de sócio recebido',
        body=SUBSCRIPTION_CONFIRMATION_MESSAGE,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscription_data['Email']],
    )
    email.attach_alternative(html_body, 'text/html')
    email.send()
