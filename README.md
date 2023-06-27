# auto-correct-slack

A Slack bot that corrects your spelling mistakes automatically.

## Environment Variables

- FIX_MODE_TYPES: Select one of the following. (default: "ALL_REPLACE")
  - "ALL_REPLACE": Replace your message with the corrected one.
  - "LINEWISE_REPLACE": Replace your message with the corrected one line by line. Your original line will be kept if there is no correction. Otherwise, your original line will be strikethroughed and corrected one be appended.
  - "LINEWISE_DIFF": Replace your message with the corrected one line by line with diff.
- MARK_MODE_TYPES: Select one of the following. (default: "ROBOT_ICON")
  - "ROBOT_ICON": Add a robot icon to the corrected message to show others that your message is corrected by a bot.
  - "NONE": Do nothing.

- SLACK_USER_TOKEN: Slack user token. (required)
- SLACK_USER_ID: Slack user ID. (required)
- OPENAI_API_KEY: OpenAI API key. (required)
- OPENAI_MODEL_NAME: OpenAI model name. (default: "gpt-4")
