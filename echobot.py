import os
import pymumble_py3
import time
import threading
import logging
from OpenSSL import crypto

logging.basicConfig(level=logging.INFO)

class MumbleEchoBot:
    def __init__(self, server, port, username, password, channel):
        # Set up certificate and key files for this bot
        self.certfile = "mumble-echo-bot_cert.crt"
        self.keyfile = "mumble-echo-bot_key.key"
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.channel = channel

        # Generate certificate and key if not already present
        self.generate_cert_and_key()

        # Initialize Mumble client connection with certificates
        self.connect_mumble()

    def generate_cert_and_key(self):
        """Generate a self-signed certificate and key if they don't already exist."""
        if not os.path.exists(self.certfile) or not os.path.exists(self.keyfile):
            logging.info("Generating self-signed certificate and key for mumble-echo-bot...")

            # Generate a private key
            key = crypto.PKey()
            key.generate_key(crypto.TYPE_RSA, 2048)

            # Create a self-signed certificate
            cert = crypto.X509()
            cert.get_subject().C = "US"
            cert.get_subject().ST = "California"
            cert.get_subject().L = "Los Angeles"
            cert.get_subject().O = "MumbleEchoBot"
            cert.get_subject().OU = "IT"
            cert.get_subject().CN = "mumble-echo-bot"
            cert.set_serial_number(1001)  # Ensure a unique serial number
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)  # 10 years validity
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(key)
            cert.sign(key, 'sha256')

            # Save the key and certificate to files
            with open(self.certfile, "wt") as cert_file:
                cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode('utf-8'))

            with open(self.keyfile, "wt") as key_file:
                key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf-8'))

            logging.info(f"Certificate and key generated for mumble-echo-bot at {self.certfile} and {self.keyfile}.")
        else:
            logging.info("Using existing certificate and key for mumble-echo-bot.")

    def connect_mumble(self):
        """Connect to the Mumble server and join the specified channel."""
        logging.info("Connecting to the Mumble server...")
        self.mumble = pymumble_py3.Mumble(self.server, self.username, password=self.password, port=self.port, reconnect=True, certfile=self.certfile, keyfile=self.keyfile)
        self.mumble.set_receive_sound(True)
        self.mumble.callbacks.set_callback(pymumble_py3.constants.PYMUMBLE_CLBK_SOUNDRECEIVED, self.on_voice_received)

        # Start the Mumble connection
        self.mumble.start()

        # Wait until the bot is ready
        while not self.mumble.is_ready():
            time.sleep(1)

        # Join the specified channel
        if self.channel:
            self.mumble.channels.find_by_name(self.channel).move_in()

        logging.info(f"Bot connected to server: {self.server} in channel: {self.channel}")

    def on_voice_received(self, user, sound_packet):
        """Callback when the bot receives a voice packet, echo it back."""
        logging.info(f"Voice received from user: {user['name']}")
        self.mumble.sound_output.add_sound(sound_packet.pcm)

    def handle_disconnect(self):
        """Monitor the connection and attempt to reconnect if disconnected."""
        while True:
            if not self.mumble.is_alive():
                logging.warning("Connection lost. Attempting to reconnect...")
                self.connect_mumble()
            time.sleep(5)  # Check connection status every 5 seconds

    def run(self):
        """Keep the bot running and handle reconnections."""
        threading.Thread(target=self.handle_disconnect, daemon=True).start()
        while True:
            time.sleep(1)

if __name__ == "__main__":
    # Configuration for your Mumble bot
    server = "localhost"  # Replace with your server's hostname or IP
    port = 6969  # Mumble default port
    username = "EchoBot"
    password = "mumblepassword."  # Add the server password if any
    channel = "Test"  # Replace with the channel name where you want the bot to join

    # Create and run the echo bot
    echo_bot = MumbleEchoBot(server, port, username, password, channel)
    echo_bot.run()
