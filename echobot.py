import pymumble_py3
import time
import threading

class MumbleEchoBot:
    def __init__(self, server, port, username, password, channel):
        # Initialize Mumble client connection
        self.mumble = pymumble_py3.Mumble(server, username, password=password, port=port, reconnect=True)
        self.mumble.set_receive_sound(True)
        self.mumble.callbacks.set_callback(pymumble_py3.constants.PYMUMBLE_CLBK_SOUNDRECEIVED, self.on_voice_received)

        # Start the Mumble connection
        self.mumble.start()
        self.mumble.is_ready()

        # Join the specified channel
        if channel:
            self.mumble.channels.find_by_name(channel).move_in()

        print(f"Bot connected to server: {server} in channel: {channel}")

    def on_voice_received(self, user, sound_packet):
        """Callback when the bot receives a voice packet, echo it back."""
        print(f"Voice received from user: {user['name']}")
        self.mumble.sound_output.add_sound(sound_packet.pcm)

    def run(self):
        """Keep the bot running."""
        while True:
            time.sleep(1)

if __name__ == "__main__":
    # Configuration for your Mumble bot
    server = "localhost"  # Replace with your server's hostname or IP
    port = 6969  # Mumble default port
    username = "EchoBot"
    password = "mumblepassword"  # Add the server password if any
    channel = "echotest"  # Replace with the channel name where you want the bot to join

    # Create and run the echo bot
    echo_bot = MumbleEchoBot(server, port, username, password, channel)
    echo_bot.run()
