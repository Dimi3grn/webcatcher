from telethon.sync import TelegramClient
from telethon import events
import asyncio
import json
import os
from datetime import datetime
import signal_parser  # Import our signal parser module

# Your API credentials
api_id = 26563174  # Your API ID
api_hash = '8f768043aaa5edb9bbb95bd0bed7e3c8'  # Your API hash

# Session name (can be any string)
session_name = 'monitor_session'

# Output files
raw_messages_file = 'telegram_trades_raw.json'  # All messages
signals_file = 'telegram_signals.json'  # Only trading signals

# Channel to monitor
channel_id = -1002217244224  # The Mr.SniperFx channel ID

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
        
        # Create output files if they don't exist
        for file_path in [raw_messages_file, signals_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
        
        # Load existing signals to avoid duplicates
        with open(signals_file, 'r') as f:
            existing_signals = json.load(f)
        existing_ids = set(item['id'] for item in existing_signals)
        
        # Set up event handler for new messages
        @client.on(events.NewMessage(chats=channel_id))
        async def handler(event):
            message = event.message
            
            # Skip if we've already processed this message
            if message.id in existing_ids:
                return
            
            # Base message data
            message_data = {
                'id': message.id,
                'date': str(message.date),
                'text': message.text,
                'timestamp': str(datetime.now())
            }
            
            # Save all messages to raw file
            with open(raw_messages_file, 'r') as f:
                raw_data = json.load(f)
            raw_data.append(message_data)
            with open(raw_messages_file, 'w') as f:
                json.dump(raw_data, f, indent=2)
            
            # Check if this is a trading signal
            if signal_parser.is_trading_signal(message.text):
                # Parse the signal and add parsed data
                parsed_signal = signal_parser.parse_signal(message.text)
                message_data['parsed'] = parsed_signal
                
                # Save to signals file if confidence is high enough
                if parsed_signal['confidence'] >= 0.4:  # Require at least symbol, direction, and one price
                    with open(signals_file, 'r') as f:
                        signals_data = json.load(f)
                    signals_data.append(message_data)
                    with open(signals_file, 'w') as f:
                        json.dump(signals_data, f, indent=2)
                    
                    # Update our tracking set
                    existing_ids.add(message.id)
                    
                    print(f"Trading signal saved: {message.text[:50]}...")
                    print(f"Parsed: {json.dumps(parsed_signal, indent=2)}")
                else:
                    print(f"Low confidence signal detected (not saved): {message.text[:50]}...")
            else:
                print(f"Message received (not a signal): {message.text[:50]}...")
        
        # Run until disconnected
        print("Monitoring for new messages... (Press Ctrl+C to stop)")
        await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())