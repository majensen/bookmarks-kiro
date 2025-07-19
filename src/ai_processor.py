import logging
import re
from typing import Dict, List, Optional
import json

from config import (
    AI_PROVIDER, AI_MODEL, AI_API_KEY, AI_TEMPERATURE, AI_MAX_TOKENS,
    DESCRIPTION_LENGTH
)

logger = logging.getLogger(__name__)

class AIProcessor:
    """Handles AI-powered content summarization and tagging with configurable providers."""
    
    def __init__(self):
        self.provider = AI_PROVIDER
        self.model = AI_MODEL
        self.temperature = AI_TEMPERATURE
        self.max_tokens = AI_MAX_TOKENS
        
        if self.provider == 'openai':
            import openai
            if not AI_API_KEY or AI_API_KEY == 'sk-test-key-placeholder':
                logger.warning("OpenAI API key not configured - using mock responses for testing")
                self.client = None  # Will use mock responses
            else:
                self.client = openai.OpenAI(api_key=AI_API_KEY)
            
        elif self.provider == 'anthropic':
            import anthropic
            if not AI_API_KEY:
                raise ValueError("Anthropic API key not configured")
            self.client = anthropic.Anthropic(api_key=AI_API_KEY)
            
        elif self.provider == 'local':
            import openai
            from config import AI_BASE_URL
            self.client = openai.OpenAI(
                base_url=AI_BASE_URL,
                api_key="not-needed"  # Local models don't need API keys
            )
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")
    
    def process_content(self, title: str, content: str, authors: List[str] = None, publisher: str = '', existing_tags: str = '') -> Dict[str, any]:
        """
        Generate summary and tags for content.
        
        Returns:
            Dict with 'description', 'tags', and 'author' keys
        """
        try:
            prompt = self._build_prompt(title, content, authors or [], publisher, existing_tags)
            
            # Mock response for testing when no API key is configured
            if self.client is None:
                result = self._generate_mock_response(title, content)
                return self._parse_ai_response(result)
            
            if self.provider in ['openai', 'local']:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes web content and extracts relevant tags, with special attention to people mentioned."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                result = response.choices[0].message.content.strip()
                
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system="You are a helpful assistant that summarizes web content and extracts relevant tags, with special attention to people mentioned.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result = response.content[0].text.strip()
            
            return self._parse_ai_response(result)
            
        except Exception as e:
            logger.error(f"AI processing failed: {e}")
            return {
                'description': f"Content from: {title}",
                'tags': [],
                'author': ', '.join(authors) if authors else ''
            }
    
    def _build_prompt(self, title: str, content: str, authors: List[str], publisher: str, existing_tags: str) -> str:
        """Build the prompt for AI processing."""
        
        # Truncate content if too long
        max_content_length = 2000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        existing_info = f"\nExisting tags: {existing_tags}" if existing_tags and existing_tags != 'NA' else ""
        author_info = f"\nDetected authors: {', '.join(authors)}" if authors else ""
        publisher_info = f"\nPublisher: {publisher}" if publisher else ""
        
        prompt = f"""
Please analyze this web content and provide:

1. A concise summary ({DESCRIPTION_LENGTH})
2. Relevant tags (1-4 words each, maximum 5 tags)
3. The author of the content (if identifiable)

**Important Guidelines:**
- Pay special attention to people mentioned in the content. Include person names as tags when they are central to the content.
- In the description, focus on the CONTENT and KEY INSIGHTS only
- Do NOT mention the author name, title, or publication in the description
- Do NOT repeat information that will be captured separately in author/title fields
- Focus on what the content discusses, argues, or reveals
- Use a NEUTRAL, OBJECTIVE tone - avoid promotional language, superlatives, or subjective opinions
- Present information factually without editorial commentary

Title: {title}
Content: {content}{existing_info}{author_info}{publisher_info}

Please respond in this exact JSON format:
{{
    "description": "Your summary here focusing only on content insights and key points",
    "tags": ["tag1", "tag2", "Person Name", "tag4"],
    "author": "Author Name (or empty string if not identifiable)"
}}
"""
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, any]:
        """Parse AI response into structured data."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                # Validate structure
                if 'description' in data and 'tags' in data:
                    # Clean and validate tags
                    tags = []
                    for tag in data['tags']:
                        if isinstance(tag, str) and len(tag.strip()) > 0:
                            # Limit tag length to 4 words
                            tag_words = tag.strip().split()
                            if len(tag_words) <= 4:
                                tags.append(' '.join(tag_words))
                    
                    # Extract author
                    author = data.get('author', '').strip()
                    
                    return {
                        'description': data['description'].strip(),
                        'tags': tags[:5],  # Limit to 5 tags
                        'author': author
                    }
            
            # Fallback parsing if JSON fails
            lines = response.strip().split('\n')
            description = ""
            tags = []
            author = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('Description:') or line.startswith('Summary:'):
                    description = line.split(':', 1)[1].strip()
                elif line.startswith('Tags:'):
                    tag_text = line.split(':', 1)[1].strip()
                    tags = [t.strip() for t in tag_text.split(',') if t.strip()]
                elif line.startswith('Author:'):
                    author = line.split(':', 1)[1].strip()
            
            return {
                'description': description or "Content summary not available",
                'tags': tags[:5],
                'author': author
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return {
                'description': "Content summary not available",
                'tags': [],
                'author': ""
            }
    
    def _generate_mock_response(self, title: str, content: str) -> str:
        """Generate a mock response for testing purposes."""
        # Extract first few sentences for a basic summary
        sentences = content.split('.')[:3]
        mock_description = '. '.join(sentences).strip()
        if len(mock_description) > 200:
            mock_description = mock_description[:200] + "..."
        
        # Generate basic tags from title
        title_words = title.lower().split()
        mock_tags = [word for word in title_words if len(word) > 3][:3]
        
        return f'''{{
    "description": "{mock_description}",
    "tags": {mock_tags},
    "author": "Test Author"
}}'''