import tkinter as tk
import socket
import asyncio
import time  # Import the time module for rate limiting
from ports import common_ports  # Import the common_ports list from ports.py

class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Port Scanner")

        self.target_label = tk.Label(root, text="Enter Target IP:")
        self.target_label.pack(pady=10)

        self.target_input = tk.Entry(root)
        self.target_input.pack(fill=tk.BOTH, padx=10, pady=5)

        self.scan_button = tk.Button(root, text="Scan Ports", command=self.on_scan)
        self.scan_button.pack(pady=10)

        self.result_label = tk.Label(root, text="", wraplength=300)
        self.result_label.pack(pady=5)

        # Create a text widget for the console
        self.console = tk.Text(root, background="black", fg="green", wrap=tk.WORD, height=10)
        self.console.pack(fill=tk.BOTH, padx=10, pady=5)

    def log_to_console(self, text):
        self.console.insert(tk.END, text + "\n")
        self.console.see(tk.END)  # Auto-scroll to the end
        self.root.update()  # Update the GUI to reflect changes

    async def scan_ports_async(self, target, port_range):
        open_ports = []

        for port in port_range:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((target, port))

                if result == 0:
                    open_ports.append(port)
                    self.log_to_console(f"Scanning port {port}... Port is open")

                sock.close()
            except (socket.timeout, socket.error, ConnectionRefusedError, Exception) as e:
                self.log_to_console(f"Error scanning port {port}: {str(e)}")

            time.sleep(0.1)  # Introduce a small delay (e.g., 100 milliseconds) between scans

        return open_ports

    def on_scan(self):
        try:
            target_host = self.target_input.get()

            # Create an asyncio event loop
            loop = asyncio.get_event_loop()

            # Divide the common_ports list into chunks for concurrent scanning
            num_chunks = 4  # You can adjust this value
            chunk_size = len(common_ports) // num_chunks
            chunks = [common_ports[i:i+chunk_size] for i in range(0, len(common_ports), chunk_size)]

            self.log_to_console("Scanning started...")

            # Use asyncio.gather to run multiple scans concurrently
            tasks = [self.scan_ports_async(target_host, chunk) for chunk in chunks]
            results = loop.run_until_complete(asyncio.gather(*tasks))

            open_ports = [port for result in results for port in result]

            if open_ports:
                self.result_label.config(text="Open ports: " + ", ".join(map(str, open_ports)))
                self.log_to_console("Scan completed. Open ports: " + ", ".join(map(str, open_ports)))
            else:
                self.result_label.config(text="No open ports found.")
                self.log_to_console("Scan completed. No open ports found.")

        except Exception as e:
            print("Error:", e)
            self.result_label.config(text="An error occurred. Please check console.")
            self.log_to_console("An error occurred. Please check console.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()
