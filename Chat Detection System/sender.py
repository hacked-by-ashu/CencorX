import tkinter as tk
import socket
import threading

def send_message():
    message = message_entry.get()
    client_socket.sendall(message.encode())
    chat_window.insert(tk.END, f"You: {message}\n")
    message_entry.delete(0, tk.END)

def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if message == "NICK":
                client_socket.sendall(nickname.encode())
            else:
                chat_window.config(state='normal')
                chat_window.insert(tk.END, message + "\n")
                chat_window.config(state='disabled')
                chat_window.see('end')
        except:
            print("An error occurred!")
            client_socket.close()
            break

def setup_connection():
    global client_socket, nickname
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1.', int(receiver_port.get())))

    # Get the nickname from the user
    nickname = nickname_entry.get()
    client_socket.sendall(f"NICK {nickname}".encode())

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.start()

# GUI Setup
root = tk.Tk()
root.title("Sender (Transmitter)")

frame = tk.Frame(root)
frame.pack(pady=10)

receiver_ip = tk.StringVar()
receiver_port = tk.StringVar()
nickname = tk.StringVar()

tk.Label(frame, text="Receiver IP:").grid(row=0, column=0)
tk.Entry(frame, textvariable=receiver_ip).grid(row=0, column=1)

tk.Label(frame, text="Port:").grid(row=1, column=0)
tk.Entry(frame, textvariable=receiver_port).grid(row=1, column=1)

tk.Label(frame, text="Nickname:").grid(row=2, column=0)
nickname_entry = tk.Entry(frame, textvariable=nickname)
nickname_entry.grid(row=2, column=1)

tk.Button(frame, text="Connect", command=setup_connection).grid(row=3, column=0, columnspan=2)

chat_window = tk.Text(root, height=20, width=50)
chat_window.pack(pady=10)

message_entry = tk.Entry(root, width=40)
message_entry.pack(side=tk.LEFT, padx=10)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(side=tk.RIGHT)

root.mainloop()