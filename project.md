Senior AI Engineer – Home Assignment
Fitbit Conversational AI POC

Fitbit envisions empowering users to make healthier lifestyle choices through personalized and engaging experiences. To further this mission, Fitbit plans to integrate a conversational AI assistant into the Fitbit app. The assistant should:

Drive daily user engagement

Offer personalized, data-driven health insights

Build trust and ongoing dialogue between Fitbit and its users

As a Senior AI Engineer, you are tasked with designing and prototyping a Conversational AI Framework to power this assistant.

Assignment Overview

You are to create a Conversational AI Framework and a working POC that meets the basic goals of the attached PRD. The assistant should demonstrate how Fitbit can:

Engage with users around their health data

Provide relevant insights

Offer helpful follow-up suggestions

Deliverables

Technical Design Document (1–2 pages)
Base your design on the Product Requirements at the end of this document. Include:

High-level architecture of the assistant

LLM orchestration framework (LangChain, LangGraph, etc.)

Data storage (for PRD-listed data inputs and conversation data)

Prompt strategy and agent behavior

Evaluation and monitoring strategy for production

Working Code (GitHub repo or zip file)

Use the Anthropic API key provided (sent through email, $5 limit)

Provide a simple working prototype of the assistant (CLI, notebook, or API-based)

The notebook should not contain the entire codebase. Codebase should be modular and resemble normal development practices. Notebook is only for interacting with the agent.

Simulate interaction using mock Fitbit health data (steps, heart rate, sleep, goals)

Demonstrate a few conversation turns showing:

Personalized insight

Follow-up questions or nudges

Handling of a simple user query

Productization Plan

Steps required to move the assistant to production

Thoughts on edge cases, real-time data integration, and scaling

Opportunities for improvement and research (e.g., personalization, multi-modal inputs, clinical validation)

Evaluation Criteria

Technical depth and soundness of the solution

Clarity and scalability of the design

Code quality and modularity

Creativity and relevance of assistant’s responses

Awareness of production concerns (privacy, monitoring, improvement loops)

Product Requirements
Overview

This document outlines the requirements for a proof-of-concept conversational AI assistant to be integrated into the Fitbit app. Its primary function is to enhance user engagement through personalized, data-driven interactions related to health, fitness, and wellness.

Goals

Personalized Engagement: Deliver tailored health insights based on Fitbit data.

Conversational Interface: Allow natural user interaction with the assistant.

Actionable Insights: Provide meaning and advice, not just raw data.

Example: “Your resting heart rate has improved—keep up the increased cardio!”

Lightweight and Extensible: Support future use cases such as:

Proactive nudges by agents

Deeper integration with clinical data

Multi-modal inputs (voice, text, wearables)

Key Features for POC

User Query Understanding
Handle natural language questions such as:

“How did I sleep last night?”

“Am I more active this week than last week?”

“What can I do to improve my heart rate variability?”

Health Insight Generation
Use data from:

Step count

Heart rate (resting, active)

Sleep duration and quality

Follow-up & Suggestions
Provide nudges such as:

“Would you like a breathing exercise to help you wind down tonight?”

“You're close to your weekly goal—want a reminder to walk this evening?”

Non-Functional Requirements

Performance & Latency

Responses must be generated within 2 seconds for most queries.

Support at least 100 concurrent users without performance drop.

Reliability

Target ≥99% uptime during POC.

Handle errors gracefully with fallback responses.

Observability

Log user queries, responses, and response time for monitoring/debugging.

Include basic analytics to review assistant behavior and identify failure patterns.

Maintainability

Code should be modular and well-documented.

Table of Contents

Fitbit Conversational AI POC

Assignment Overview

Evaluation Criteria

Product Requirements

Overview

Goals

Key Features for POC

Non-Functional Requirements