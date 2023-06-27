# auto-correct-slack

A Slack bot that corrects your spelling mistakes automatically.

# 


AI will rewrite your message in seconds!

![demo_before](https://github.com/hmirin/SlackAutoCorrectionBot/assets/1284876/924a9e68-1f5c-4fb5-b119-32fa30a9f500)
![demo_after](https://github.com/hmirin/SlackAutoCorrectionBot/assets/1284876/c448c7a9-36b0-4c0d-8046-9b81a4f87f2a)

I'm prone to making spelling mistakes. I'm also a lazy person. So I made this bot to correct my spelling mistakes automatically.


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

# Deployment

- Use [fly.io](https://fly.io/) to deploy this bot.
- Set the environment variables above in the fly.io's dashboard.