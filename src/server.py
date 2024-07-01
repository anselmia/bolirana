from flask import Flask, request, jsonify
import logging

app = Flask(__name__)
external_queue = None
pin_states = {}


def set_queue(q):
    global external_queue
    external_queue = q


@app.route("/receive_data", methods=["POST"])
def receive_data():
    pin = request.form.get("pin")
    state = request.form.get("state")
    logging.info(f"Received: Pin - {pin}, State - {state}")
    if pin not in pin_states or state != pin_states[pin]:
        pin_states[pin] = state
        if external_queue and state == "HIGH":
            external_queue.put((pin, state))
        return jsonify({"status": "success", "message": f"State updated to {state}"})
    return jsonify({"status": "ignored", "message": "No change detected"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=False, host="0.0.0.0", port=5000)
