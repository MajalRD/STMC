import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import logging
import os
import datetime

class Alert:
    def __init__(self, password="hqqqeydhyhmvzaem"):
        self.username = "dogdetectionberkane@gmail.com"
        self.appPassword = password
        self.smtp = None

        self.logging = logging.getLogger("Alert Logger")
        self.logging.setLevel(logging.ERROR)
        
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler('logs/alert_logfile.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        
        self.logging.addHandler(file_handler)
        self.gps = []

    def login(self):
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(self.username, self.appPassword)

    def connect(self):
        try:
            self.login()
        except smtplib.SMTPServerDisconnected as e:
            self.logging.error(f"Server is disconnected, trying to reconnect {e}")
            self.login()
        except smtplib.SMTPException:
            print("Authentication error")

    def prepare_massage(self, mean_conf, CAM_ID, end_clock):
        message = MIMEMultipart()
        message["from"] = "Berkane Horde Alert System"

        date = end_clock.strftime("%Y-%m-%d %H:%M:%S")
        text = f"Horde detectée \n Certitude : {mean_conf}% \nDate : {date}\nCamera ID: {CAM_ID} \nLocation GPS: 34.92726380065734, -2.3367654438991754 \n\n\n© MAJAL Berkane 2023 :\n W. AMARA, W. RABHI et F. EL JAIMI \nSupervised by: Dr Z. CHAROUH"
        message["subject"] = f"BHAS Cam {CAM_ID}"
        message.attach(MIMEText(text))
        return message
    
    def send_message(self, CAM_ID, saved_img, end_clock, mean_conf, receivers,nbr):
        try:
            message = self.prepare_massage(mean_conf, CAM_ID, end_clock)
            with open(saved_img, "rb") as img:
                img_data = img.read()
            image = MIMEImage(img_data)
            file_name = f"{end_clock} ALERT {nbr}.jpg"
            image.add_header('Content-Disposition', 'attachment', filename=file_name)

            message.attach(image)
            message.add_header('Content-Disposition', "attachment, filename= test_img.jpg")

            self.logging.info("sending mail...")
            
            for receiver in receivers:
                self.smtp.sendmail(self.username, receiver, message.as_string())
                print(f"mail sent to {receiver}")

            # delete the saved image
            os.remove(saved_img)
        except smtplib.SMTPServerDisconnected as e:
            self.logging.error(f"Server is disconnected, trying to reconnect {e}")
            self.login()
            self.logging.info("Reconnected succussfully")

            message = self.prepare_massage(mean_conf, CAM_ID)

            message.attach(MIMEImage(Path(saved_img).read_bytes()))

            #Sending the message
            for receiver in receivers:
                message["to"] = receiver
                self.smtp.send_message(message)
        except smtplib.SMTPConnectError as e:
            self.logging.error(f"Error connecting to the SMTP server: {e}")

        except smtplib.SMTPAuthenticationError as e:
            self.logging.error(f"Error authenticating with the SMTP server: {e}")

        except Exception as e:
            self.logging.error(f"Error sending the email: {e}")



    # # def send_alert(self, CAM_ID, saved_img, date, mean_conf, receivers, nbr):
    # #     try:
    # #         message = self.prepare_massage(mean_conf, CAM_ID)
    # #         with open(saved_img, "rb") as img:
    # #             img_data = img.read()
    # #         image = MIMEImage(img_data)
    # #         file_name = f"{date} ALERT {nbr}.jpg"
    # #         image.add_header('Content-Disposition', 'attachment', filename=file_name)

    # #         message.attach(image)
    # #         message.add_header('Content-Disposition', "attachment, filename= test_img.jpg")

    # #         print("sending mail...")

    # #         #Sending the message
    # #         for receiver in receivers:
    # #             message["to"] = receiver
    # #             self.smtp.send_message(message)
    # #             print(f"mail sent to {receiver}")
    # #         # delete the saved image
    # #         os.remove(saved_img)
    # #     except smtplib.SMTPServerDisconnected as e:
    # #         self.logging.error(f"Server is disconnected, trying to reconnect {e}")
    # #         self.login()
    # #         self.logging.info("Reconnected succussfully")

    # #         message = self.prepare_massage(mean_conf, CAM_ID)

    # #         message.attach(MIMEImage(Path(saved_img).read_bytes()))

    # #         #Sending the message
    # #         for receiver in receivers:
    # #             message["to"] = receiver
    # #             self.smtp.send_message(message)
    # #     except smtplib.SMTPConnectError as e:
    # #         self.logging.error(f"Error connecting to the SMTP server: {e}")

    # #     except smtplib.SMTPAuthenticationError as e:
    # #         self.logging.error(f"Error authenticating with the SMTP server: {e}")

    # #     except Exception as e:
    # #         self.logging.error(f"Error sending the email: {e}")

