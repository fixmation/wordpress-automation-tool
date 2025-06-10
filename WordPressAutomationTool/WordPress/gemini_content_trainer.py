
"""
Gemini Content Trainer Module

This module provides training contexts and prompts for the Gemini AI model
to generate website content based on specific categories and menu structures.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class GeminiContentTrainer:
    """
    Trains and provides context to Gemini AI for generating category-specific content.
    """
    
    def __init__(self):
        """Initialize the content trainer with category-specific templates."""
        # Category-specific training data and content templates
        self.category_templates = {
            'eCommerce': {
                'tone': 'professional and persuasive',
                'focus': 'product benefits, features, and calls-to-action',
                'structure': 'short paragraphs, bullet points for features, clear pricing',
                'keywords': ['shop', 'purchase', 'quality', 'shipping', 'secure', 'cart'],
                'content_examples': [
                    "Our premium products are crafted with attention to detail and made from high-quality materials that ensure durability and satisfaction.",
                    "Shop our new collection featuring exclusive designs you won't find anywhere else. Each item comes with our satisfaction guarantee."
                ]
            },
            'Restaurant': {
                'tone': 'inviting and appetizing',
                'focus': 'menu highlights, atmosphere, dining experience',
                'structure': 'descriptive food paragraphs, highlight specials, location and hours',
                'keywords': ['fresh', 'delicious', 'chef', 'ingredients', 'menu', 'reservation'],
                'content_examples': [
                    "Our chef crafts each dish using locally-sourced ingredients, bringing farm-fresh flavors directly to your table in a warm, inviting atmosphere.",
                    "Experience our signature dishes prepared with traditional recipes and modern techniques, paired perfectly with our curated wine selection."
                ]
            },
            'Blog': {
                'tone': 'conversational and engaging',
                'focus': 'valuable information, personal insights, reader engagement',
                'structure': 'catchy intro, substantive middle with subheadings, engaging conclusion',
                'keywords': ['discover', 'insights', 'tips', 'experience', 'learn', 'perspective'],
                'content_examples': [
                    "In this post, we'll explore practical strategies you can implement today to improve your productivity and achieve better work-life balance.",
                    "My recent experience with this approach completely changed how I view the process. Here's what I learned and how you can apply it too."
                ]
            },
            'Portfolio': {
                'tone': 'professional and confident',
                'focus': 'skills, accomplishments, unique value proposition',
                'structure': 'concise project descriptions, results-oriented content, testimonials',
                'keywords': ['expertise', 'projects', 'skills', 'experience', 'results', 'clients'],
                'content_examples': [
                    "With over a decade of experience in the industry, I bring a unique perspective to each project, focusing on both aesthetic appeal and functional design.",
                    "This award-winning project demonstrates my approach to solving complex challenges through innovative thinking and technical expertise."
                ]
            },
            'Business': {
                'tone': 'authoritative and trustworthy',
                'focus': 'services, expertise, client benefits',
                'structure': 'clear service descriptions, company values, client testimonials',
                'keywords': ['solutions', 'professional', 'reliable', 'expertise', 'service', 'results'],
                'content_examples': [
                    "Our team of certified professionals delivers customized solutions that address your specific business challenges and drive measurable results.",
                    "Since 2005, we've helped over 500 businesses improve their operations through our comprehensive consulting services and dedicated support."
                ]
            },
            'News': {
                'tone': 'informative and objective',
                'focus': 'timely information, facts, relevant context',
                'structure': 'inverted pyramid style, quotes, supporting details',
                'keywords': ['breaking', 'report', 'announced', 'development', 'official', 'source'],
                'content_examples': [
                    "In a recent announcement, officials confirmed the new policy will take effect next month, impacting thousands of residents in the affected areas.",
                    "The latest data shows a significant shift in market trends, with analysts pointing to several key factors driving this unexpected change."
                ]
            },
            'Social Network': {
                'tone': 'friendly and inclusive',
                'focus': 'community features, interaction opportunities, user benefits',
                'structure': 'welcoming intro, feature highlights, community guidelines',
                'keywords': ['connect', 'share', 'community', 'members', 'profile', 'interact'],
                'content_examples': [
                    "Join our growing community where you can connect with like-minded individuals, share your experiences, and participate in engaging discussions.",
                    "Our platform provides powerful tools to help you build meaningful connections while maintaining control over your privacy and personal data."
                ]
            },
            'Educational': {
                'tone': 'instructive and encouraging',
                'focus': 'learning opportunities, educational value, student outcomes',
                'structure': 'clear program descriptions, learning objectives, student resources',
                'keywords': ['learn', 'courses', 'skills', 'certificate', 'training', 'development'],
                'content_examples': [
                    "Our accredited courses are designed by industry experts to provide you with practical skills that directly apply to current market demands.",
                    "Students gain access to comprehensive learning materials, interactive workshops, and one-on-one mentoring sessions throughout the program."
                ]
            },
            'Real Estate': {
                'tone': 'professional and descriptive',
                'focus': 'property features, location benefits, investment value',
                'structure': 'compelling property descriptions, neighborhood highlights, clear contact information',
                'keywords': ['property', 'location', 'features', 'spacious', 'opportunity', 'quality'],
                'content_examples': [
                    "This exceptional property features three bedrooms, two bathrooms, and a newly renovated kitchen, all situated in a highly sought-after neighborhood with top-rated schools.",
                    "Located just minutes from downtown, this charming home offers the perfect balance of urban convenience and peaceful suburban living."
                ]
            },
            'Nonprofit': {
                'tone': 'compassionate and inspiring',
                'focus': 'mission, impact, ways to get involved',
                'structure': 'compelling mission statement, success stories, clear calls to action',
                'keywords': ['mission', 'support', 'community', 'donate', 'volunteer', 'impact'],
                'content_examples': [
                    "For over 15 years, our organization has been working tirelessly to address food insecurity in underserved communities, providing over 2 million meals to families in need.",
                    "Your donation directly supports our programs, with 90% of all contributions going directly to frontline services that make a tangible difference."
                ]
            }
        }
        
        # Menu-specific content guidance
        self.menu_content_mapping = {
            'Home': {
                'purpose': 'Introduce the website and organization with compelling overview',
                'content_type': 'Overview, mission statement, unique value proposition',
                'example': "Welcome to [Business Name], where we [primary value proposition]. Since [year], we've been helping clients [primary benefit]."
            },
            'About': {
                'purpose': 'Build trust by sharing organization history, values, and team',
                'content_type': 'Company history, mission, values, team bios',
                'example': "Founded in [year], [Business Name] began with a simple mission: [mission statement]. Today, we continue to uphold our core values of [values]."
            },
            'Services': {
                'purpose': 'Detail offerings with clear benefits to potential clients',
                'content_type': 'Service descriptions, benefits, process explanations',
                'example': "Our [service name] provides comprehensive solutions for [client need]. Our process begins with [first step] and continues through [additional steps]."
            },
            'Products': {
                'purpose': 'Showcase products with compelling descriptions that drive sales',
                'content_type': 'Product descriptions, features, specifications, pricing',
                'example': "The [Product Name] features [key feature] that helps you [benefit]. Each product is [quality statement] and comes with [warranty/guarantee]."
            },
            'Portfolio': {
                'purpose': 'Demonstrate expertise through past work examples',
                'content_type': 'Project descriptions, challenges overcome, results achieved',
                'example': "For [Client Name], we created a [project type] that [key achievement]. The project involved [challenges] which we addressed by [solution]."
            },
            'Blog': {
                'purpose': 'Provide valuable content that establishes expertise',
                'content_type': 'Articles, guides, industry insights, tips',
                'example': "In this guide, we'll explore [topic] and share practical strategies for [desired outcome]. Our experience with [relevant experience] informs these recommendations."
            },
            'Contact': {
                'purpose': 'Make it easy for visitors to reach out',
                'content_type': 'Contact details, form, location information, hours',
                'example': "We'd love to hear from you! Fill out the form below or reach us directly at [contact info]. Our team is available [business hours]."
            },
            'Menu': {
                'purpose': 'Display food/drink offerings with appetizing descriptions',
                'content_type': 'Menu categories, dish descriptions, prices, specials',
                'example': "Our [dish name] features [key ingredients] prepared [cooking method], served with [sides]. All dishes use [quality statement about ingredients]."
            },
            'Events': {
                'purpose': 'Promote upcoming happenings to drive attendance',
                'content_type': 'Event listings, descriptions, dates, registration details',
                'example': "Join us for [event name] on [date] at [time]. This [event type] will feature [highlights] and provides an opportunity to [benefit of attending]."
            },
            'Gallery': {
                'purpose': 'Visually showcase work, products, or location',
                'content_type': 'Image descriptions, project contexts, captions',
                'example': "This [project/product] for [client/occasion] showcases our [skill/technique]. The [specific element] highlights our attention to [quality aspect]."
            },
            'Testimonials': {
                'purpose': 'Build credibility through client feedback',
                'content_type': 'Client quotes, project contexts, results',
                'example': '"[Business Name] delivered exceptional [service/product] that helped us [client result]." - [Client Name], [Client Position/Company]'
            },
            'FAQ': {
                'purpose': 'Address common questions to reduce barriers to conversion',
                'content_type': 'Questions and answers about products, services, policies',
                'example': "Q: How long does [process/service] typically take?\nA: Our [process/service] usually takes [timeframe], though this can vary based on [factors]."
            }
        }
    
    def get_category_prompt(self, category_name: str) -> str:
        """
        Generates a training prompt for Gemini based on the website category.
        
        Args:
            category_name: The name of the website category
            
        Returns:
            A detailed prompt instructing Gemini how to generate content for this category
        """
        if category_name not in self.category_templates:
            logger.warning(f"Unknown category '{category_name}'. Using generic prompt.")
            return self._get_generic_category_prompt()
        
        template = self.category_templates[category_name]
        prompt = f"""
        You are generating content for a {category_name} website. 
        
        Content Guidelines:
        - Tone: {template['tone']}
        - Focus: {template['focus']}
        - Structure: {template['structure']}
        - Include some of these relevant keywords: {', '.join(template['keywords'])}
        
        Content should be specific to the {category_name} industry and avoid generic platitudes.
        
        Examples of good content for this category:
        1. "{template['content_examples'][0]}"
        2. "{template['content_examples'][1]}"
        
        Generate original, engaging content that follows these guidelines and avoids vague statements.
        Be specific about the business, its offerings, and benefits to visitors.
        """
        return prompt
    
    def get_menu_prompt(self, menu_item: str) -> str:
        """
        Generates a prompt for content specific to a menu item/page.
        
        Args:
            menu_item: The name of the menu item/page
            
        Returns:
            A prompt instructing how to generate content for this menu page
        """
        normalized_menu = next((k for k in self.menu_content_mapping.keys() 
                               if k.lower() == menu_item.lower()), None)
        
        if not normalized_menu:
            logger.warning(f"Unknown menu item '{menu_item}'. Using generic prompt.")
            return self._get_generic_menu_prompt(menu_item)
        
        template = self.menu_content_mapping[normalized_menu]
        prompt = f"""
        You are generating content for the '{normalized_menu}' page of a website.
        
        Page Purpose: {template['purpose']}
        
        Content Type: {template['content_type']}
        
        Example Structure: {template['example']}
        
        Create specific, purposeful content for this '{normalized_menu}' page that avoids generic statements.
        The content should clearly fulfill the purpose of this page type and provide value to visitors.
        """
        return prompt
    
    def get_combined_prompt(self, category_name: str, menu_items: List[Dict]) -> str:
        """
        Generates a comprehensive prompt combining category and menu structure.
        
        Args:
            category_name: The website category
            menu_items: List of menu items with their details
            
        Returns:
            A comprehensive prompt for generating website content
        """
        category_prompt = self.get_category_prompt(category_name)
        
        menu_structure = "\n".join([
            f"- {item['label']}: {item.get('description', 'No description')}"
            for item in menu_items if 'label' in item
        ])
        
        return f"""
        {category_prompt}
        
        Website Menu Structure:
        {menu_structure}
        
        Generate a cohesive set of content for this {category_name} website that aligns with its menu structure.
        Each page's content should:
        1. Be specifically tailored to the {category_name} industry
        2. Fulfill the purpose of that specific page type
        3. Maintain consistent branding and messaging across pages
        4. Include specific details rather than generic statements
        5. Address the needs and interests of the target audience
        
        Avoid:
        - Generic platitudes that could apply to any business
        - Vague statements without specific value propositions
        - Inconsistent tone or messaging between pages
        - Content that doesn't align with the {category_name} industry
        
        The content should feel custom-created for this specific business, not applicable to any generic website.
        """
    
    def _get_generic_category_prompt(self) -> str:
        """Returns a generic prompt when category is unknown."""
        return """
        Create specific, engaging website content that:
        - Has a clear purpose and audience focus
        - Includes specific details about offerings and benefits
        - Uses a consistent, appropriate tone
        - Avoids generic statements that could apply to any business
        
        The content should feel customized to this specific business and industry.
        """
    
    def _get_generic_menu_prompt(self, menu_item: str) -> str:
        """Returns a generic prompt for an unknown menu item."""
        return f"""
        Create specific content for the '{menu_item}' page that:
        - Clearly communicates the purpose of this page
        - Provides valuable information to visitors
        - Uses a consistent tone with the rest of the website
        - Includes specific details rather than generic statements
        
        The content should be tailored to this specific page purpose and the overall website goals.
        """
    
    def get_image_description_prompt(self, category_name: str, page_type: str) -> str:
        """
        Generates a prompt for creating image descriptions based on category and page type.
        
        Args:
            category_name: The website category
            page_type: The type of page (home, about, etc.)
            
        Returns:
            A prompt for generating appropriate image descriptions
        """
        category_specific = ""
        if category_name in self.category_templates:
            category_specific = f"""
            For a {category_name} website, imagery should emphasize:
            - {self.category_templates[category_name]['focus']}
            - Visual elements that convey: {self.category_templates[category_name]['tone']}
            """
        
        return f"""
        Create a detailed image description for a {page_type} page on a {category_name} website.
        
        {category_specific}
        
        Your description should:
        1. Be specific enough to guide a designer or AI image generator
        2. Include details about recommended style, composition, and elements
        3. Align with the brand tone and message of a {category_name} website
        4. Be practical and realistic for a professional business website
        
        Avoid generic descriptions that could apply to any website.
        """
