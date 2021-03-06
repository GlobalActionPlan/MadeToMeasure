from pyramid_mailer.interfaces import IMailer


class PrintingMailer(object): #pragma : no cover
    """
    Dummy mailing instance. Simply prints all messages directly instead of handling them.
    Good for avoiding mailing users when you want to test things locally.
    """

    def send(self, message):    
        """
        Send, but really print content of message
        """
        
        print "Subject: %s" % message.subject
        print "To: %s" % ", ".join(message.recipients)
        print "==== HTML Output =================================="
        print message.html
        print "==== Plantext Output =============================="
        print message.body

    send_to_queue = send_immediately = send


def includeme(config): #pragma : no cover
    print "\n === WARNING! Using printing mailer - no mail will be sent! ===\n"
    mailer = PrintingMailer()
    config.registry.registerUtility(mailer, IMailer)
