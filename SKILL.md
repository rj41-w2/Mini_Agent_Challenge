# Skill: The Sentiment Sorter

## Intent
Analyze user text input and determine its emotional tone.

## Rules
1. Accept a single sentence input from the user.
2. Send the text to an LLM API with a strict system prompt.
3. The LLM output MUST be exactly one word: POSITIVE or NEGATIVE.
4. If the captured word is NEGATIVE, trigger a sympathetic print response.