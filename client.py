""" run a client that connects to a server and interacts with user using tkinter """
import constants
from cryptography.fernet import Fernet
import re
import requests
import tkinter as tk


def encrypt_message(message: str) -> bytes:
    """
    Encrypts a message
    :param message: a regular message
    :return: the encrypted message
    """
    key = constants.key
    f = Fernet(key)
    message = message.encode()
    encrypted_message = f.encrypt(message)
    return encrypted_message


def decrypt_message(encrypted_message: bytes) -> bytes:
    """
    Decrypts an encrypted message
    :param encrypted_message: the encrypted message to decrypt
    :return: the decrypted message
    """
    key = constants.key
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)
    return decrypted_message


def download(outputlabel: tk.Label) -> None:
    """
    download a requested file from the server's files to a requested location
    :param outputlabel: the label where that response of server is written
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
    outputlabel['text'] = f"file downloaded successfully to {path}"


def upload(outputlabel: tk.Label) -> None:
    """
    upload a requested file to the server
    :param outputlabel: the label where that response of server is written
    """
    path = constants.request.split("- ")
    path = path[-1]
    with open(path, 'r') as file:
        request = constants.request.split("/")
        name = request[-1]
        start = True
        for chunk in file:
            if start == True:
                requests.put(f"http://{constants.ip}:{constants.port}/upload/{name}?q=w", data=encrypt_message(chunk))
                start = False
            else:
                requests.put(f"http://{constants.ip}:{constants.port}/upload/{name}/", data=encrypt_message(chunk))
    outputlabel['text'] = "file uploaded successfully"


def regular(outputlabel: tk.Label) -> None:
    """
    show the output of a requested linux terminal command by sending it to server and getting output
    :param outputlabel: the label where that response of server is written
    """
    request = encrypt_message(constants.request.split("- ")[-1])
    response = requests.put(f"http://{constants.ip}:{constants.port}/regular/", data=request)
    content = response.content
    content = decrypt_message(content).decode('unicode_escape')
    outputlabel['text'] = f"output:\n{content}"


def main() -> None:
    """ Run interactive tkinter client """
    root = tk.Tk()
    canvas1 = tk.Canvas(root, width=800, height=300)
    canvas1.pack()
    outputlabel = tk.Label(root, text="")
    outputlabel.config(font=('helvetice', 14))
    outputlabel.pack(side="left")
    commandentry = tk.Entry(root, width=80)
    canvas1.create_window(400, 200, window=commandentry)
    button1 = tk.Button(text="run command", command=lambda: send_command(commandentry, outputlabel))
    canvas1.create_window(400, 250, window=button1)

    label1 = tk.Label(root, text="run a command")
    label1.config(font=('helvetica', 30))
    canvas1.create_window(400, 60, window=label1)

    label2 = tk.Label(root, text="type the command here:")
    label2.config(font=('helvetica', 22))
    canvas1.create_window(400, 150, window=label2)
    root.mainloop()


def send_command(commandentry: tk.Entry, outputlabel: tk.Label) -> None:
    """
    send the command the user enters to server and present output using tkinter
    :param commandEntry: the tkinter entry in which the user writes the command
    :param outputlabel: the label where that response of server is written
    """
    dict = {"download": download, "upload": upload, "command": regular}
    request = commandentry.get()
    constants.request = request
    x = re.search('upload|download|command', request)
    dict[x.group()](outputlabel)


if __name__ == "__main__":
    main()
