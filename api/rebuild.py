"""
Vercel serverless function — triggered daily at 04:00 UTC by the cron in vercel.json.
Triggers a rebuild of the site by calling Vercel's Deploy Hooks API.
"""
import os
import urllib.request
import json


def handler(request):
    hook = os.environ.get("VERCEL_DEPLOY_HOOK_URL", "")
    if not hook:
        return {"statusCode": 500, "body": json.dumps({"error": "No deploy hook configured"})}
    try:
        req = urllib.request.Request(hook, method="POST")
        urllib.request.urlopen(req, timeout=10)
        return {"statusCode": 200, "body": json.dumps({"ok": True, "message": "Rebuild triggered"})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
