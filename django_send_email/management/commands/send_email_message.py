"""
Management command to send email using Django settings
"""
import os
import sys
from optparse import make_option

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.mail import EmailMessage

try:
    from django.utils.six.moves import input as raw_input
except ImportError:
    pass


CONFIRM_MESSAGE = '''
---------- MESSAGE FOLLOWS ----------
Subject: {subject}
From: {from_email}
To: {recipient_list_formatted}
Cc: {cc_formatted}

{message}
------------ END MESSAGE ------------
'''


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--noinput',
            action='store_false',
            dest='interactive',
            default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'
        ),
        make_option(
            '-f', '--from',
            dest='from_email',
            default=None,
            help='Email address to use to send emails from. Defaults to use settings.DEFAULT_FROM_EMAIL'
        ),
        make_option(
            '-r', '--raise-error',
            action='store_true',
            dest='fail_silently',
            default=False,
            help='Exceptions during the email sending process will be raised. Default to failing silently'
        ),
        make_option(
            '-n', '--noprefix',
            action='store_true',
            dest='noprefix',
            default=False,
            help='Disables email subject prefix. Default behavior is to prepend settings.EMAIL_SUBJECT_PREFIX'
        ),
        make_option(
            '-b', '--bcc',
            dest='bcc',
            default=None,
            help='Comma separated list of email addresses for BCC'
        ),
        make_option(
            '-c', '--cc',
            dest='cc',
            default=None,
            help='Comma separated list of email addresses for CC'
        ),
    )
    args = '<subject> <message or file or "-"> <recipient1>...<recipientN>'
    help = 'Sends an email to the specified email addresses. \nMessage can be a string, filename or "-" to read from stdin.'

    def handle_send_mail(self, args, options):
        verbosity = int(options.get('verbosity', 1))

        if len(args) < 3:
            raise CommandError('Subject, message and at least one recipient are required')

        (subject, message), recipients = args[:2], args[2:]

        if os.path.isfile(message):
            # Read message from file
            try:
                message = open(message).read()
            except (IOError, OSError) as exc:
                raise CommandError('Error reading message file "{}": {}'.format(message, exc))
        elif message == '-':
            # Read message from sys.stdin
            message = sys.stdin.read()
            options['interactive'] = False

        options['message'] = message

        recipient_list = list(recipients)
        get_addresses = lambda l: [a[1] for a in getattr(settings, l, ())]

        for copy in ('bcc', 'cc'):
            if options[copy]:
                options[copy] = [a.strip() for a in options[copy].split(',')]

        for lst in (recipient_list, options['bcc'], options['cc']):
            if not lst:
                continue
            for recipient in lst:
                if recipient in ('ADMINS', 'MANAGERS'):
                    lst.remove(recipient)
                    lst.extend(get_addresses(recipient))

            for recipient in lst:
                try:
                    validate_email(recipient)
                except ValidationError:
                    raise CommandError('"{}" is not a valid email address'.format(recipient))

        options['recipient_list'] = recipient_list
        options['subject'] = '{}{}'.format('' if options['noprefix'] else settings.EMAIL_SUBJECT_PREFIX, subject)

        if options['from_email'] is None:
            options['from_email'] = settings.DEFAULT_FROM_EMAIL

        if verbosity > 1 or options['interactive']:
            for lst in ('recipient_list', 'cc'):
                options['{}_formatted'.format(lst)] = ', '.join(options[lst] or [])
            self.stdout.write(CONFIRM_MESSAGE.format(**options))

        if options['interactive']:
            if raw_input('Send email message? [Y/n] ').lower().startswith('n'):
                self.stderr.write('Operation cancelled.\n')
                sys.exit(1)

        EmailMessage(
            subject=options['subject'],
            body=options['message'],
            from_email=options['from_email'],
            to=options['recipient_list'],
            bcc=options['bcc'],
            cc=options['cc']
        ).send(fail_silently=options['fail_silently'])

        if verbosity > 1:
            self.stdout.write('Message sent\n')

    def handle(self, *args, **options):
        try:
            self.handle_send_mail(args, options)
        except KeyboardInterrupt:
            self.stderr.write('Operation cancelled.\n')
            sys.exit(1)
