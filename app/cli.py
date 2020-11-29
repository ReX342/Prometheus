# from app import app
# import smtplib, ssl
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart

# sender_email = "rex@zerofox.xyz"
# receiver_email = "occ.rex@gmail.com"
# password = input("Type your password and press enter:")

# message = MIMEMultipart("alternative")
# message["Subject"] = "Learning to program"
# message["From"] = sender_email
# message["To"] = receiver_email
# message["Reply-To"] = sender_email


# # Create the plain-text and HTML version of your message
# text = """\
# Click below to activate your profile
# {{ url_activate }} """
# html = render_template("activate_mail.html.j2")


# # Turn these into plain/html MIMEText objects
# part1 = MIMEText(text, "plain")
# part2 = MIMEText(html, "html")

# # Add HTML/plain-text parts to MIMEMultipart message
# # The email client will try to render the last part first
# message.attach(part1)
# message.attach(part2)

# # Create secure connection with server and send email
# context = ssl.create_default_context()
# with smtplib.SMTP_SSL("mail.gandi.net", 465, context=context) as server:
#     server.login(sender_email, password)
#     server.sendmail(
#         sender_email, receiver_email, message.as_string()
#     )
# #  Use below/delete below?
# @app.cli.command()
# def send_verification_emails():
#     """sends verification emails"""
#     print("print sending verification emails")