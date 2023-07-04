from typing import Literal
from flask import Flask, request, make_response
import json
import openai
from slack_sdk import WebClient
import os
import sys
import logging
import threading
import difflib

app = Flask(__name__)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

FIX_MODE_TYPES = Literal["LINEWISE_DIFF", "LINEWISE_REPLACE", "ALL_REPLACE"]
MARK_MODE_TYPES = Literal["ROBOT_ICON", "NONE"]

SLACK_USER_TOKEN = os.environ.get("SLACK_USER_TOKEN")
SLACK_USER_ID = os.environ.get("SLACK_USER_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4")

slack_web_client = WebClient(token=SLACK_USER_TOKEN)
FIX_MODE: FIX_MODE_TYPES = os.environ.get("FIX_MODE", "ALL_REPLACE")
MARK_MODE: MARK_MODE_TYPES = os.environ.get("MARK_MODE", "ROBOT_ICON")

ENABLE_FOR_DM = os.environ.get("ENABLE_FOR_DM", "1").lower() == "1"
ENABLE_FOR_CHANNEL = os.environ.get("ENABLE_FOR_CHANNEL", "1").lower() == "1"


def one_line_diff(str1, str2):
    diff = difflib.ndiff(str1, str2)
    result = ""
    temp_str_added = ""
    temp_str_removed = ""
    for d in diff:
        if d[0] == "+":
            temp_str_added += d[2:]
        elif d[0] == "-":
            temp_str_removed += d[2:]
        else:
            if temp_str_removed:
                if temp_str_removed.strip():
                    if MARK_MODE == "ROBOT_ICON":
                        result += f" 🤖 ~{temp_str_removed}~ "
                    else:
                        result += f" ~{temp_str_removed}~ "
                temp_str_removed = ""
            if temp_str_added:
                if MARK_MODE == "ROBOT_ICON":
                    result += f" 🤖 {temp_str_added} "
                else:
                    result += f"{temp_str_added}"
                temp_str_added = ""
            result += d[2:]
    # add any remaining changes at the end
    if temp_str_removed:
        if temp_str_removed.strip():
            if MARK_MODE == "ROBOT_ICON":
                result += f" 🤖 ~{temp_str_removed}~ "
            else:
                result += f" ~{temp_str_removed}~ "
    if temp_str_added:
        if MARK_MODE == "ROBOT_ICON":
            result += f" 🤖 {temp_str_added} "
        else:
            result += f"{temp_str_added}"
    return result


def call_fix(text):
    gpt_res = openai.ChatCompletion.create(
        model=OPENAI_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "You're a corrector bot. You reply to user's messages with corrected versions of them. Return corrected message only. If you find the message correct, return the message iteself. Only correct misspelling, grammar.",
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.1,
        max_tokens=int(len(text) * 1.2),
    )
    app.logger.info("chatGPT respsonse " + json.dumps(gpt_res))
    return gpt_res.get("choices")[0].get("message").get("content").strip()


def check_line(line):
    if (
        line.startswith("~")
        or line.startswith(">")
        or line.startswith("<")
        or line.startswith("`")
    ):
        return False
    # ignore if url
    if line.startswith("http"):
        return False
    return True


def worker(event):
    user_message = event.get("text").strip()
    if user_message.endswith("🤖"):
        return
    if FIX_MODE == "ALL_REPLACE":
        rewritten_message = call_fix(user_message)
        if user_message == rewritten_message:
            return
        slack_web_client.chat_update(
            channel=event.get("channel"),
            text=rewritten_message + " 🤖",
            ts=event.get("ts"),  # timestamp of the message to edit
        )
    elif FIX_MODE in ["LINEWISE_DIFF", "LINEWISE_REPLACE"]:
        lines = user_message.split("\n")
        rewritten_message = []
        for idx, line in enumerate(lines):
            rewritten_message.append(line)
            if check_line(line):
                # fix line
                app.logger.info("Fixing line: " + line)
                rewritten_line = call_fix(line)
                if line == rewritten_line:
                    continue
                if FIX_MODE == "LINEWISE_REPLACE":
                    rewritten_message[-1] = "~" + line + "~"
                    if MARK_MODE == "ROBOT_ICON":
                        rewritten_message.append(f"🤖 {rewritten_line}")
                    else:
                        rewritten_message.append(rewritten_line)
                else:
                    rewritten_message[-1] = one_line_diff(line, rewritten_line)

        updated_text = "\n".join(rewritten_message)
        slack_web_client.chat_update(
            channel=event.get("channel"),
            text=updated_text,
            ts=event.get("ts"),  # timestamp of the message to edit
        )


@app.route("/slack", methods=["POST"])
def slack_event():
    data = json.loads(request.data)

    if "challenge" in data:
        app.logger.info("Responsed to challenge")
        return make_response(
            data.get("challenge"),
            200,
        )

    if "event" in data:
        event = data.get("event")
        if (
            event.get("type") == "message"
            and "subtype" not in event
            and event.get("user") == SLACK_USER_ID
        ):
            # ignore if bot is disabled for DM (not self DM)
            if event.get("channel_type") == "im" and not ENABLE_FOR_DM:
                return make_response("", 200)
            # ignore if bot is disabled for channel
            if event.get("channel_type") == "channel" and not ENABLE_FOR_CHANNEL:
                return make_response("", 200)
            # silently mark not to trigger bot
            if "\u200b" in event.get("text"):
                return make_response("", 200)

            app.logger.info("API called with " + json.dumps(data))

            worker(event)  # TODO: make this async
            return make_response("", 200)

    return make_response("", 200)


if __name__ == "__main__":
    app.run(port=3000)
