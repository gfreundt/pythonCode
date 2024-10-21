# TODO: fix to work with outlook
# TODO: send confirmation email

from gft_utils import EmailUtils


def process(db_cursor, monitor):
    """Check inbox for unsubscribe/resubscribe requests and switch table in database."""

    # log start of process
    monitor.log("Checking for Sub/Unsub requests.")

    # get all emails in inbox
    email_account = "servicioalertasperu@outlook.com"
    email = EmailUtils(account=email_account)
    _inbox = email.read_outlook(fr=email_account, only_unread=True, mark_read=False)

    # create lists of email addresses of requests to unsubscribe or resuscribe from unread emails
    unsub_emails = []
    sub_emails = []
    for email in _inbox:
        for m in email.messages:
            # register sender to use as key to change flag
            sender = m.sender.split("<")[1][:-1] if "<" in m.sender else ""
            # load subject and body text
            sub = m.subject.split(f"<{email_account}>")[0] if m.subject else ""
            body = m.body.split(f"<{email_account}>")[0] if m.body else ""
            # check if request in subject or body, not case-sensitive
            if "ELIMINAR" in sub.upper() or "ELIMINAR" in body.upper():
                unsub_emails.append(sender)
                email.markAsRead()
            elif "INGRESAR" in sub.upper() or "INGRESAR" in body.upper():
                sub_emails.append(sender)
                email.markAsRead()

    # move from active members to past members
    for unsub in unsub_emails:
        cmd = f"INSERT INTO pastMembers SELECT * FROM members WHERE Correo='{unsub}'; DELETE FROM members WHERE Correo='{unsub}'"
        db_cursor.executescript(cmd)
        monitor.log(f"Removed members with email {unsub} from active member list.")

    # move from past members to active members
    for sub in sub_emails:
        cmd = f"INSERT INTO members SELECT * FROM pastMembers WHERE Correo='{unsub}'; DELETE FROM pastMembers WHERE Correo='{unsub}'"
        db_cursor.executescript(cmd)
        monitor.log(f"Reinstated members with email {unsub} into active member list.")

    # add counter to monitor display
    monitor.log(
        f"Total Unsubs: {len(unsub_emails)} - Total Resubs: {len(sub_emails)}", type=1
    )
