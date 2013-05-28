# Email Command for Django

This app provides a simple management command for sending emails using your Django settings from the command line.


## Install

Pull down the app:

    $ pip install django-send-email

Add it to your `INSTALLED_APPS`:

    INSTALLED_APPS = (
      ...
      'django_send_email'
    )


## Sending Emails

django-send-email provides a management command named `send_email_message` to send emails from the command line.

    $ django-admin.py send_email_message subject message user1@example.com user2@example.com

Subject, message and at least one recipient are required. You can pass `ADMINS` or `MANAGERS` as any one of the recipients and django-send-email will fetch the recipients from the proper Django setting.

    $ django-admin.py send_email_message subject message MANAGERS --bcc=ADMINS

You can also pass a filename as the message argument and django-send-email will use the file contents at the body of the email.

    $ django-admin.py send_email_message subject /path/to/message.txt user1@example.com user2@example.com

Alternatively you can use `-` as the message argument to read from standard input.

    $ django-admin.py send_email_message subject - user1@example.com user2@example.com < /path/to/message.txt
    $ echo "some message text" | django-admin.py send_email_message subject - user1@example.com user2@example.com

### Full Usage

    Usage: manage.py send_email_message [options] <subject> <message or file or "-"> <recipient1>...<recipientN>

    Sends an email to the specified email addresses.
    Message can be a string, filename or "-" to read from stdin.

    Options:
      -v VERBOSITY, --verbosity=VERBOSITY
                            Verbosity level; 0=minimal output, 1=normal output,
                            2=verbose output, 3=very verbose output
      --settings=SETTINGS   The Python path to a settings module, e.g.
                            "myproject.settings.main". If this isn't provided, the
                            DJANGO_SETTINGS_MODULE environment variable will be
                            used.
      --pythonpath=PYTHONPATH
                            A directory to add to the Python path, e.g.
                            "/home/djangoprojects/myproject".
      --traceback           Print traceback on exception
      --noinput             Tells Django to NOT prompt the user for input of any
                            kind.
      -f FROM_EMAIL, --from=FROM_EMAIL
                            Email address to use to send emails from. Defaults to
                            use settings.DEFAULT_FROM_EMAIL
      -r, --raise-error     Exceptions during the email sending process will be
                            raised. Default to failing silently
      -n, --noprefix        Disables email subject prefix. Default behavior is to
                            prepend settings.EMAIL_SUBJECT_PREFIX
      -b BCC, --bcc=BCC     Comma separated list of email addresses for BCC
      -c CC, --cc=CC        Comma separated list of email addresses for CC
      --version             show program's version number and exit
      -h, --help            show this help message and exit


## Testing

Running the unittests is as simple as testing any other Django app

    django-admin.py test django_send_email

To test the command on a development SMTP server, you can run the debug SMTP server from the `smtp` library.

    $ python -m smtpd -n -c DebuggingServer localhost:1025

Just make sure that Django is configured correctly to point at localhost:1025