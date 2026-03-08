"""eBay Trading API integration for ending listings."""

import logging
import xml.etree.ElementTree as ET

import requests

from config import EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID, EBAY_SANDBOX, EBAY_USER_TOKEN

logger = logging.getLogger(__name__)

API_URL = (
    "https://api.sandbox.ebay.com/ws/api.dll"
    if EBAY_SANDBOX
    else "https://api.ebay.com/ws/api.dll"
)


def end_listing(listing_id, reason="NotAvailable"):
    """End an eBay listing via the Trading API.

    Args:
        listing_id: The eBay item/listing ID.
        reason: EndingReason - NotAvailable, Incorrect, LostOrBroken, OtherListingError, SellToHighBidder.

    Returns:
        dict with success status and details.
    """
    if not all([EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID, EBAY_USER_TOKEN]):
        return {"success": False, "error": "eBay API credentials not configured"}

    headers = {
        "X-EBAY-API-SITEID": "3",  # UK
        "X-EBAY-API-COMPATIBILITY-LEVEL": "1349",
        "X-EBAY-API-CALL-NAME": "EndItem",
        "X-EBAY-API-APP-NAME": EBAY_APP_ID,
        "X-EBAY-API-DEV-NAME": EBAY_DEV_ID,
        "X-EBAY-API-CERT-NAME": EBAY_CERT_ID,
        "Content-Type": "text/xml",
    }

    body = f"""<?xml version="1.0" encoding="utf-8"?>
<EndItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
    <RequesterCredentials>
        <eBayAuthToken>{EBAY_USER_TOKEN}</eBayAuthToken>
    </RequesterCredentials>
    <ItemID>{listing_id}</ItemID>
    <EndingReason>{reason}</EndingReason>
</EndItemRequest>"""

    try:
        response = requests.post(API_URL, headers=headers, data=body, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"ebay": "urn:ebay:apis:eBLBaseComponents"}
        ack = root.find("ebay:Ack", ns)

        if ack is not None and ack.text in ("Success", "Warning"):
            logger.info("Successfully ended eBay listing %s", listing_id)
            return {"success": True, "listing_id": listing_id}

        errors = root.findall("ebay:Errors", ns)
        error_msgs = []
        for error in errors:
            msg = error.find("ebay:LongMessage", ns)
            if msg is not None:
                error_msgs.append(msg.text)

        error_detail = "; ".join(error_msgs) if error_msgs else "Unknown error"
        logger.error("Failed to end eBay listing %s: %s", listing_id, error_detail)
        return {"success": False, "error": error_detail}

    except requests.RequestException as e:
        logger.error("eBay API request failed: %s", e)
        return {"success": False, "error": str(e)}


def get_listing_status(listing_id):
    """Check the current status of an eBay listing."""
    if not all([EBAY_APP_ID, EBAY_CERT_ID, EBAY_DEV_ID, EBAY_USER_TOKEN]):
        return {"success": False, "error": "eBay API credentials not configured"}

    headers = {
        "X-EBAY-API-SITEID": "3",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "1349",
        "X-EBAY-API-CALL-NAME": "GetItem",
        "X-EBAY-API-APP-NAME": EBAY_APP_ID,
        "X-EBAY-API-DEV-NAME": EBAY_DEV_ID,
        "X-EBAY-API-CERT-NAME": EBAY_CERT_ID,
        "Content-Type": "text/xml",
    }

    body = f"""<?xml version="1.0" encoding="utf-8"?>
<GetItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
    <RequesterCredentials>
        <eBayAuthToken>{EBAY_USER_TOKEN}</eBayAuthToken>
    </RequesterCredentials>
    <ItemID>{listing_id}</ItemID>
    <DetailLevel>ReturnAll</DetailLevel>
</GetItemRequest>"""

    try:
        response = requests.post(API_URL, headers=headers, data=body, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.text)
        ns = {"ebay": "urn:ebay:apis:eBLBaseComponents"}
        ack = root.find("ebay:Ack", ns)

        if ack is not None and ack.text in ("Success", "Warning"):
            item = root.find("ebay:Item", ns)
            status = item.find("ebay:SellingStatus/ebay:ListingStatus", ns)
            title = item.find("ebay:Title", ns)
            return {
                "success": True,
                "listing_id": listing_id,
                "status": status.text if status is not None else "Unknown",
                "title": title.text if title is not None else "Unknown",
            }

        return {"success": False, "error": "Failed to get listing status"}

    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
