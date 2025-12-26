import json
import uuid
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone

from .models import Conversation, Message
# Import the agent graph - we need to make sure agent.py is importable
# We'll need to modify agent.py slightly to expose a runable function that doesn't use the CLI loop
from agent import app as agent_app
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')
        self.user_group_name = f"chat_{self.conversation_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message')
        
        # 1. Save User Message
        user_msg_obj = await self.save_message(self.conversation_id, 'user', message_content)
        
        # 2. Update Title if needed (async wrapper needed?)
        await self.update_conversation_title_if_needed(self.conversation_id, message_content)

        # 3. Retrieve Conversation History for Agent
        history = await self.get_conversation_history(self.conversation_id)
        
        # 4. Invoke Agent
        # Prepare inputs
        inputs = {"messages": history}
        
        # Stream response
        # Using aconfig to ensure async compat or just run in executors if agent is sync
        # LangGraph app.stream is usable.
        
        ai_response_content = ""
        
        try:
            # We'll stream chunks. 
            # Note: app.stream yields state updates. Getting partial tokens might need specific LLM stream config.
            # For this setup, we will just send the final response or intermediate tool calls.
            # For better UX, we'd want streaming tokens, but LangGraph defaults to state updates.
            
            final_state = await sync_to_async(agent_app.invoke)(inputs)
            
            # Extract only the NEW messages
            # The agent might return multiple messages (tool calls + final answer)
            
            # Simple logic: get the last message
            last_message = final_state['messages'][-1]
            
            if isinstance(last_message, AIMessage):
                ai_response_content = last_message.content
                
                # Send back to WebSocket
                await self.send(text_data=json.dumps({
                    'type': 'ai_response',
                    'message': ai_response_content,
                    'is_final': True
                }))
                
                # Save AI Message
                await self.save_message(self.conversation_id, 'ai', ai_response_content)
                
        except Exception as e:
            logger.error(f"Error in agent execution: {e}")
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))


    @sync_to_async
    def save_message(self, conversation_id, sender, content):
        conversation = Conversation.objects.get(id=conversation_id)
        msg = Message.objects.create(conversation=conversation, sender=sender, content=content)
        conversation.save() # Update updated_at
        return msg

    @sync_to_async
    def update_conversation_title_if_needed(self, conversation_id, content):
        conversation = Conversation.objects.get(id=conversation_id)
        if conversation.title == "New Conversation":
            # Use first 30 chars
            conversation.title = (content[:30] + '..') if len(content) > 30 else content
            conversation.save()

    @sync_to_async
    def get_conversation_history(self, conversation_id):
        conversation = Conversation.objects.get(id=conversation_id)
        messages = conversation.messages.all().order_by('timestamp')
        
        # Convert DB messages to LangChain messages
        lc_messages = []
        for msg in messages:
            if msg.sender == 'user':
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.sender == 'ai':
                lc_messages.append(AIMessage(content=msg.content))
        
        return lc_messages
