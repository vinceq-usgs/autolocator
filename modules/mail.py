#! /usr/local/bin/python3

from modules.config import config

use_sendmail=False

def dyfimail(p):
    """
Simple interface to send mail. Subject, to, and from have default
values which may be overridden.

Usage:
    from mail import dyfimail
    dyfimail({'subject':'x','to':'recipient','text':'body'})

    """

    msgsubj='DYFI Autolocator Alert'
    msgfrom=config.mail['operator']
    msgto=config.mail['to']

    if 'subject' in p:
        msgsubj=p['subject']
    if 'to' in p:
        msgto=p['to']

    if use_sendmail:
        sendmail(p)
        return

    from subprocess import Popen,PIPE
    print('Mailer:subj:',msgsubj)
    print('Mailer:to:',msgto)

    command=[config.mail['mailbin'],'-s','"'+msgsubj+'"']
    if 'attachment' in p:
        command.append('-a')
        command.append(p['attachment'])
    command.append(msgto)

    print('Mail command:',command)
    mailer=Popen(
            command,
            stdin=PIPE,universal_newlines=True
            )
    mailer.communicate(p['text'])

def sendmail(p):
    import smtplib
    from email.mime.text import MIMEText
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEImage import MIMEImage

    msg=MIMEText(p['text'])
    msg['Subject']=msgsubj
    msg['From']=msgfrom
    msg['To']=msgto
    print('Sending:')
    print(msg)

    if 'attachment' in p:
        pass

    s=smtplib.SMTP(config.mail['smtp'])
    s.set_debuglevel(1)
    s.send_message(msg)
    print(s)
    s.quit()

    return


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(
        description='Access the DYFI main function.'
    )
    parser.add_argument('--subject',type=str,
        help="Subject line")
    parser.add_argument('--to',type=str,
        help="Recipient (default is DEFAULT_RECIPIENT)")
    parser.add_argument('text',type=str,
        help="Body of message")
    args=parser.parse_args()

    p={}
    if args.subject:
        p['subject']=args.subject
    if args.to:
        p['to']=args.to
    p['text']=args.text
    dyfimail(p)

