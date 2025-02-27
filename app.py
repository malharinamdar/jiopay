import streamlit as st
import asyncio
from app1 import JioPayScraper, JioPayChatbot  # Import from app1.py

# Set up the app
st.set_page_config(page_title="JioPay Assistant", page_icon="🤖")

def initialize_session_state():
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'messages' not in st.session_state:
        st.session_state.messages = []

@st.cache_resource(show_spinner=False)
def setup_chatbot_sync():
    """Runs the async setup in a synchronous way"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(setup_chatbot())

async def setup_chatbot():
    """Cache the chatbot setup to avoid re-initialization on every reload"""
    scraper = JioPayScraper()
    chatbot = JioPayChatbot()
    
    with st.spinner("Scraping latest JioPay information..."):
        scraped_data = await scraper.scrape_all()
    
    if not scraped_data:
        st.error("Failed to scrape data. Please check the connection and try again.")
        return None
    
    with st.spinner("Creating knowledge base..."):
        chatbot.create_knowledge_base(scraped_data)
        chatbot.initialize_qa()
    
    return chatbot

def main():
    initialize_session_state()
    
    st.title("JioPay Customer Support Assistant")
    st.markdown("Ask me anything about JioPay services!")

    # Initialize chatbot once
    if not st.session_state.initialized:
        with st.spinner("Initializing assistant..."):
            st.session_state.chatbot = setup_chatbot_sync()
            if st.session_state.chatbot:
                st.session_state.initialized = True
                if not st.session_state.messages:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Welcome to JioPay Support! How can I help you today?"
                    })

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("View Sources"):
                    st.markdown(f"Sources: {message['sources']}")

    # Chat interface
    if st.session_state.initialized:
        user_input = st.chat_input("Ask your question about JioPay...")
        
        if user_input:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get assistant response
            response = st.session_state.chatbot.ask(user_input)
            
            # Process response for sources
            if "Sources:" in response:
                answer, sources = response.split("Sources:", 1)
                answer = answer.strip()
                sources = sources.strip()
            else:
                answer = response
                sources = None
            
            # Add assistant response to chat history
            assistant_message = {"role": "assistant", "content": answer}
            if sources:
                assistant_message["sources"] = sources
            st.session_state.messages.append(assistant_message)
            
            # Rerun to update the chat display
            st.rerun()

if __name__ == "__main__":
    main()
