import queue
import threading
from src.game import Game
from src.server import app, set_queue

# Create a shared queue
shared_queue = queue.Queue()

# Set the shared queue in the server module
set_queue(shared_queue)

if __name__ == "__main__":
    game = Game(shared_queue)  # Pass the queue to the game constructor if needed

    # Start the Flask app on a separate thread
    flask_thread = threading.Thread(
        target=lambda: app.run(debug=False, host="0.0.0.0", port=5000)
    )
    flask_thread.start()

    game.run()
