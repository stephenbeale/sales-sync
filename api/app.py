"""Sales Sync API — cross-platform listing sync between Vinted and eBay."""

import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import GMAIL_POLL_INTERVAL
from models import (
    add_item,
    add_sync_log,
    delete_item,
    find_item_by_vinted_title,
    get_item,
    get_items,
    get_sync_logs,
    init_db,
    mark_sold,
    update_item,
)
from services.ebay_service import end_listing, get_listing_status
from services.email_service import check_for_sales

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000"])


@app.before_request
def before_first_request():
    init_db()


# --- Item CRUD ---


@app.route("/api/items", methods=["GET"])
def list_items():
    status = request.args.get("status")
    items = get_items(status=status)
    return jsonify(items)


@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    item = add_item(
        title=data["title"],
        ebay_listing_id=data.get("ebay_listing_id"),
        vinted_title=data.get("vinted_title"),
    )
    add_sync_log(item["id"], "created", "manual")
    return jsonify(item), 201


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_single_item(item_id):
    item = get_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.route("/api/items/<int:item_id>", methods=["PUT"])
def update_single_item(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    allowed = {"title", "ebay_listing_id", "vinted_title"}
    updates = {k: v for k, v in data.items() if k in allowed}

    item = update_item(item_id, **updates)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item)


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def remove_item(item_id):
    item = get_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    delete_item(item_id)
    return jsonify({"success": True})


# --- Sell / Sync actions ---


@app.route("/api/items/<int:item_id>/sell", methods=["POST"])
def sell_item(item_id):
    """Mark an item as sold. Optionally end the eBay listing."""
    data = request.get_json() or {}
    sold_on = data.get("sold_on", "vinted")  # vinted or ebay

    item = get_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    if item["status"] == "sold":
        return jsonify({"error": "Item already sold"}), 400

    result = {"item_id": item_id, "sold_on": sold_on}

    # If sold on Vinted, try to end the eBay listing
    if sold_on == "vinted" and item.get("ebay_listing_id"):
        ebay_result = end_listing(item["ebay_listing_id"])
        result["ebay_ended"] = ebay_result["success"]
        if not ebay_result["success"]:
            result["ebay_error"] = ebay_result.get("error")
            logger.warning(
                "Failed to end eBay listing %s: %s",
                item["ebay_listing_id"],
                ebay_result.get("error"),
            )
        add_sync_log(
            item_id,
            "ebay_end_listing",
            "auto",
            f"Success: {ebay_result['success']}",
        )

    item = mark_sold(item_id, sold_on)
    add_sync_log(item_id, "marked_sold", sold_on)
    result["item"] = item

    return jsonify(result)


@app.route("/api/items/<int:item_id>/ebay-status", methods=["GET"])
def check_ebay_status(item_id):
    """Check the current eBay listing status for an item."""
    item = get_item(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    if not item.get("ebay_listing_id"):
        return jsonify({"error": "No eBay listing ID"}), 400

    status = get_listing_status(item["ebay_listing_id"])
    return jsonify(status)


# --- Email polling ---


@app.route("/api/check-emails", methods=["POST"])
def check_emails():
    """Poll Gmail for new Vinted sale notifications and auto-sync."""
    data = request.get_json() or {}
    after = data.get("after")

    sales = check_for_sales(after_timestamp=after)
    results = []

    for sale in sales:
        item = find_item_by_vinted_title(sale["item_title"])
        match_result = {
            "email_subject": sale["subject"],
            "parsed_title": sale["item_title"],
            "matched": item is not None,
        }

        if item:
            match_result["item_id"] = item["id"]
            match_result["item_title"] = item["title"]

            if item["status"] == "active":
                # Auto-sync: mark sold and end eBay listing
                if item.get("ebay_listing_id"):
                    ebay_result = end_listing(item["ebay_listing_id"])
                    match_result["ebay_ended"] = ebay_result["success"]
                    add_sync_log(
                        item["id"],
                        "ebay_end_listing",
                        "email_auto",
                        f"Success: {ebay_result['success']}",
                    )

                mark_sold(item["id"], "vinted")
                add_sync_log(item["id"], "marked_sold", "email_auto")
                match_result["auto_synced"] = True
            else:
                match_result["auto_synced"] = False
                match_result["reason"] = "Item already sold"

        results.append(match_result)

    return jsonify({"sales_found": len(sales), "results": results})


# --- Sync log ---


@app.route("/api/sync-log", methods=["GET"])
def list_sync_log():
    item_id = request.args.get("item_id", type=int)
    limit = request.args.get("limit", 50, type=int)
    logs = get_sync_logs(item_id=item_id, limit=limit)
    return jsonify(logs)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)
