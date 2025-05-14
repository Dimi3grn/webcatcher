from telethon.sync import TelegramClient
import asyncio

# Your API credentials
api_id = 26563174  # Your actual API ID 
api_hash = '8f768043aaa5edb9bbb95bd0bed7e3c8'  # Your actual API hash

# Session name (use the same as before to reuse your authentication)
session_name = 'monitor_session'

async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print("Fetching all your dialogs (channels, chats, etc.)...")
        
        # Get all dialogs
        dialogs = await client.get_dialogs()
        
        print("\nChannels you're a member of:")
        print("-" * 50)
        
        # Find the target channel (-2217244224)
        target_found = False
        
        for dialog in dialogs:
            # Only print channels (not chats or users)
            if hasattr(dialog.entity, 'broadcast') or hasattr(dialog.entity, 'megagroup'):
                entity_type = "Channel" if hasattr(dialog.entity, 'broadcast') and dialog.entity.broadcast else "Supergroup"
                print(f"ID: {dialog.id}, Name: {dialog.name}, Type: {entity_type}")
                
                # Check various ID formats
                stripped_id = abs(dialog.id)
                if stripped_id == 2217244224 or dialog.id == -2217244224 or dialog.id == -1002217244224:
                    print(f"\n*** FOUND YOUR TARGET CHANNEL: {dialog.name} ***")
                    print(f"Correct ID format: {dialog.id}")
                    print(f"Entity type: {entity_type}")
                    target_found = True
        
        if not target_found:
            print("\nCould not find your target channel. Make sure you've joined it.")
            print("Try looking through the list above for a similar channel name.")

if __name__ == '__main__':
    asyncio.run(main())