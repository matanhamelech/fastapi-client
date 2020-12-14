"""run a client that connects to a server and interacts with user using tkinter"""
import tkinter as tk
import requests
from cryptography.fernet import Fernet
import constants


def load_key():
    """Load the previously generated key"""
    return open("secret.key", "rb").read()


def encrypt_message(message):
    """
    Encrypts a message"
    :param message: a regular message
    :return: the encrypted message
    """
    key = load_key()
    f = Fernet(key)
    message = message.encode()
    encrypted_message = f.encrypt(message)
    return encrypted_message


def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    :param encrypted_message: the encrypted message to decrypt
    :return: the decrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


def download(label3):
    """
    download a requested file from the server's files to a requested location
    :param label3: the label where that response of server is written
    """
    path = constants.request
    path = path.split('/')
    filename = path[-1]
    filename = encrypt_message(filename)
    with requests.put(f"http://{constants.ip}:{constants.port}/download/", data=filename, stream=True) as response:
        path = constants.request.split("- ")
        path = path[-1]
        with open(str(path), 'w') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(decrypt_message(chunk).decode())
    label3['text'] = f"file downloaded successfully to {path}"


def upload(label3):
    """
    upload a requested file to the server
    :param label3: the label where that response of server is written
    """
    path = constants.request.split("- ")
    path = path[-1]
    with open(path, 'r') as file:
        request = constants.request.split("/")
        name = request[-1]
        i = 0
        for chunk in file:
            if i == 0:
                requests.put(f"http://{constants.ip}:{constants.port}/upload/{name}?q=w", data=encrypt_message(chunk))
            else:
                requests.put(f"http://{constants.ip}:{constants.port}/upload/{name}/", data=encrypt_message(chunk))
            i += 1
    label3['text'] = "file uploaded successfully"


def regular(label3):
    """
    show the output of a requested linux terminal command by sending it to server and getting output
    :param label3: the label where that response of server is written
    """
    request = encrypt_message(constants.request)
    response = requests.put(f"http://{constants.ip}:{constants.port}/regular/", data=request)
    content = response.content
    content = decrypt_message(content).decode('unicode_escape')
    label3['text'] = f"output:\n{content}"


def main():
    """Run interactive tkinter client"""
    root = tk.Tk()
    canvas1 = tk.Canvas(root, width=800, height=300)
    canvas1.pack()
    label3 = tk.Label(root, text="")
    label3.config(font=('helvetice', 14))
    label3.pack(side="left")
    entry1 = tk.Entry(root, width=80)
    canvas1.create_window(400, 200, window=entry1)
    button1 = tk.Button(text="run command", command=lambda: send_command(entry1, label3))
    canvas1.create_window(400, 250, window=button1)

    label1 = tk.Label(root, text="run a command")
    label1.config(font=('helvetica', 30))
    canvas1.create_window(400, 60, window=label1)

    label2 = tk.Label(root, text="type the command here:")
    label2.config(font=('helvetica', 22))
    canvas1.create_window(400, 150, window=label2)
    root.mainloop()


def send_command(entry1, label3):
    """
    send the command the user enters to server and present output using tkinter
    :param entry1: the tkinter entry in which the user writes the command
    :param label3: the label where that response of server is written
    """
    request = entry1.get()
    constants.request = request
    if request[0:8] == "download":
        download(label3)
    elif request[0:6] == "upload":
        upload(label3)
    else:
        regular(label3)


if __name__ == "__main__":
    main()
