# OKA-SAN (Tentative) - AI-Integrated Study Support Desk Lamp

## Introduction
**OKA-SAN** is a smart desk lamp designed to assist students during their study sessions by encouraging good posture, providing breaks, and ensuring focus. It runs on a Raspberry Pi embedded within the product.

### Features

1. **Posture Correction**: OKA-SAN detects when the user is slouching or sitting with poor posture and provides gentle reminders through audio and light punches to encourage better posture.
2. **Wake-Up Alerts**: If the user falls asleep while studying, OKA-SAN will wake them up with sounds and light punches.
3. **Snack Delivery**: During breaks, OKA-SAN offers a small snack to keep the user energized.
4. **Auto On/Off Lighting**: OKA-SAN detects when the user approaches the desk and automatically turns on the light. When the user leaves, the light turns off.

## Installation

Since OKA-SAN runs on a pre-installed Raspberry Pi within the desk lamp, users do not need to manually install or configure the software. This repository is provided for reference only.

## How It Works

OKA-SAN uses a combination of sensors and cameras to monitor the user’s posture and behavior. The software processes input from these sensors or cameras to determine when to activate specific features like posture correction, wake-up alerts, and automatic lighting.

1. **Posture Detection**: OKA-SAN detects the user's sitting position and assesses whether their posture is correct.
2. **Motion Sensors**: Detect when the user approaches or leaves the desk.
3. **Snack Dispenser Control**: A small motor system is used to deliver snacks during scheduled breaks.
4. **Wake-Up System**: The software triggers alarms and mild physical prompts when the user appears to be sleeping.
