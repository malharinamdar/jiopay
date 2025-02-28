import os
import asyncio

# Install Playwright browsers if not already installed
async def install_playwright():
    try:
        
        os.system("playwright install chromium --with-deps")
        print("Playwright installation attempted without sudo")
        
    except Exception as e:
        print(f"Error installing Playwright: {e}")
        # Continue anyway

from crawl4ai import AsyncWebCrawler
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
from langchain.chains import RetrievalQA
from typing import List, Dict
from langchain_text_splitters import TokenTextSplitter  # Update import
from playwright.async_api import async_playwright

async def get_browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        return browser

os.environ["OPENAI_API_KEY"] = "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"

class JioPayScraper:
    def __init__(self):
        self.crawler = AsyncWebCrawler()
        self.websites = [
            "https://www.jiopay.in/business/help-center",
            "https://www.jiopay.in/business"
        ]
    
    async def scrape_all(self) -> List[Dict]:
        """Scrape all configured websites and return extracted content."""
        results = []
        async with self.crawler as crawler:
            for url in self.websites:
                try:
                    result = await crawler.arun(
                        url=url,
                        parse_with_js=True,
                        browser="chromium",
                        browser_channel="chromium",
                        wait_for="networkidle",
                        page_timeout=120000,  # Increase overall timeout to 120 seconds
                        screenshot=False,
                        proxy="None",
                        headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                        }
                    )
                    
                    content = self.extract_content(result)
                    if content:
                        results.append({"url": url, "content": content})
                    else:
                        print(f"No content found for {url}")

                except Exception as e:
                    print(f"Error scraping {url}: {str(e)}")
                    continue
                    
        return results

    def extract_content(self, result):
        """Handle different possible content formats with fallbacks"""
        if result.extracted_content:
            return result.extracted_content
        if result.markdown:
            return result.markdown
        if result.markdown_v2:
            return result.markdown_v2.raw_markdown
        if result.html:
            return result.html
        return ""

class JioPayChatbot:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = TokenTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        self.vector_store = None
        self.qa_chain = None
    
    def create_knowledge_base(self, documents: List[Dict]):
        """Process documents and create vector store."""
        texts = [doc["content"] for doc in documents]
        metadatas = [{"source": doc["url"]} for doc in documents]
        
        docs = self.text_splitter.create_documents(texts, metadatas=metadatas)
        self.vector_store = FAISS.from_documents(docs, self.embeddings)
    
    def initialize_qa(self):
        """Initialize the QA chain with RAG using OpenAI."""
        llm = OpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo-instruct",
            max_tokens=300
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": 3, "score_threshold": 0.75}
            ),
            return_source_documents=True
        )
    
    def ask(self, question: str) -> str:
        """Get answer to user question."""
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Call initialize_qa() first.")
        
        try:
            result = self.qa_chain.invoke({"query": question})
            sources = list(set([doc.metadata["source"] for doc in result["source_documents"]]))
            return f"{result['result']}\n\nSources: {sources}"
        except Exception as e:
            return f"Error processing your question: {str(e)}"

async def async_main():
    
    scraper = JioPayScraper()
    print("Scraping JioPay websites...")
    
    try:
        scraped_data = await scraper.scrape_all()
    except Exception as e:
        print(f"Scraping failed: {str(e)}")
        return
    
    if not scraped_data:
        print("No data scraped. Exiting...")
        return
    
    chatbot = JioPayChatbot()
    print("Creating knowledge base...")
    chatbot.create_knowledge_base(scraped_data)
    
    print("Initializing QA system...")
    chatbot.initialize_qa()
    
    print("JioPay Assistant ready! Type 'exit' to quit.")
    while True:
        try:
            question = input("\nYou: ")
            if question.lower() in ['exit', 'quit']:
                break
            answer = chatbot.ask(question)
            print(f"\nAssistant: {answer}")
        except KeyboardInterrupt:
            break

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
