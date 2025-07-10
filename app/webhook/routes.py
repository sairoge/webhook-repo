from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import events_collection
from flask import render_template

webhook = Blueprint('webhook', __name__)

@webhook.route('/receiver', methods=["POST"])
def receiver():
    return {}, 200

def parse_event(event_type, data):
    timestamp = datetime.utcnow().isoformat()

    # PUSH event
    if event_type == "push":
        return {
            "request_id": data["head_commit"]["id"],
            "author": data["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,  
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": timestamp
        }
    # PULL REQUEST event
    elif event_type == "pull_request" and data["action"] == "opened":
        pr = data["pull_request"]
        return {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "PULL_REQUEST",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": timestamp
        }

    # MERGE EVENT
    elif event_type == "pull_request" and data["action"] == "closed" and data["pull_request"]["merged"]:
        pr = data["pull_request"]
        return {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "MERGE",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": timestamp
        }

    return None 

# Route to receive GitHub webhook POSTs
@webhook.route("/webhook", methods=["POST"])
def receive_webhook():
    print("Webhook received!")
    print(request.json)

    event_type = request.headers.get("X-GitHub-Event")
    data = request.json
    event = parse_event(event_type, data)

    if event:
        events_collection.insert_one(event)
        return jsonify({"status": "stored"}), 200

    return jsonify({"status": "ignored"}), 200


# Route for frontend to fetch events
@webhook.route("/events", methods=["GET"])
def get_events():
    events = list(events_collection.find({}, {"_id": 0}))  # omit _id
    return jsonify(events)

@webhook.route("/")
def index():
    return render_template("index.html")
