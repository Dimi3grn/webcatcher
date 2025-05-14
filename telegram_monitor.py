from telethon.sync import TelegramClient
from telethon import events
import asyncio
import json
import os
from datetime import datetime

# Your API credentials from https://my.telegram.org/
api_id = 26563174  # Replace with your API ID (number)
api_hash = '8f768043aaa5edb9bbb95bd0bed7e3c8'  # Replace with your API hash (string)

# Session name (can be any string)
session_name = 'monitor_session'

# Output file
output_file = 'telegram_trades.json'

# Channel to monitor (numeric ID for private channels)
channel_id = -1002217244224  # The channel ID you found

async def main():
    # Initialize with your API credentials
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("Client created")
        
        # Make sure we're connected
        if not await client.is_user_authorized():
            print("You need to log in first!")
            phone = input("Enter your phone number with country code (e.g. +15551234567): ")
            await client.send_code_request(phone)
            code = input("Enter the code you received: ")
            await client.sign_in(phone, code)
        
        # Get information about the channel
        try:
            channel = await client.get_entity(channel_id)
            print(f"Monitoring channel: {getattr(channel, 'title', 'Unknown')}")
        except Exception as e:
            print(f"Error accessing channel: {e}")
            print("Make sure you have joined this channel before running this script.")
            return
        
        # Create output file if it doesn't exist
        if not os.path.exists(output_file):
            with open(output_file, 'w') as f:
                json.dump([], f)
        
        # Set up event handler for new messages
        @client.on(events.NewMessage(chats=channel_id))
        async def handler(event):
            message = event.message
            
            # Read existing data
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            # Format message data
            message_data = {
                'id': message.id,
                'date': str(message.date),
                'text': message.text,
                'timestamp': str(datetime.now())
            }
            
            # Append new message
            data.append(message_data)
            
            # Save updated data
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"New message saved: {message.text[:50]}...")
        
        # Run until disconnected
        print("Monitoring for new messages... (Press Ctrl+C to stop)")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())