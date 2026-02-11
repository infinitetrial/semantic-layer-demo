# backend/llm_client.py
"""
LLM Client using Google AI Studio SDK
"""

import google.generativeai as genai
import json
from typing import Dict, Any
from semantic_parser import SemanticLayerParser

class LLMClient:
    """Client for Google AI Studio (Gemini)"""
    
    def __init__(self, api_key: str, semantic_parser: SemanticLayerParser):
        genai.configure(api_key=api_key)
        
        # Use a working model
        model_name = 'models/gemini-2.5-flash'  # Fixed: use full path
        print(f"\nUsing model: {model_name}")
        
        self.model = genai.GenerativeModel(model_name)
        self.parser = semantic_parser
        
        self.segments = semantic_parser.list_all_segments()
        self.metrics = semantic_parser.list_all_metrics()
    
    def build_system_prompt(self) -> str:
        segments_text = ""
        for seg_type, seg_list in self.segments.items():
            segments_text += f"\n  {seg_type}: {', '.join(seg_list)}"
        
        metrics_text = "\n  ".join(self.metrics)
        
        prompt = f"""You are a data analyst assistant that helps users query customer data using a semantic layer.

AVAILABLE CUSTOMER SEGMENTS:{segments_text}

AVAILABLE METRICS:
  {metrics_text}

Your job is to understand the user's question and return a JSON response with:
{{
  "intent": "metric_query|segment_breakdown|comparison",
  "metric": "metric_name",
  "segment_type": "segment_type_if_applicable",
  "segment": "segment_name_if_applicable",
  "comparison": {{"segment_a": {{}}, "segment_b": {{}}}}
}}

EXAMPLES:

User: "What's average spending for parents?"
Response: {{"intent": "metric_query", "metric": "total_spending", "segment_type": "family_status", "segment": "parents"}}

User: "Show me CLV by age group"
Response: {{"intent": "segment_breakdown", "metric": "customer_lifetime_value", "segment_type": "customer_age_segments"}}

User: "Compare spending for parents vs no children"
Response: {{"intent": "comparison", "metric": "total_spending", "comparison": {{"segment_a": {{"type": "family_status", "name": "parents"}}, "segment_b": {{"type": "family_status", "name": "no_children"}}}}}}

IMPORTANT: 
- Return ONLY valid JSON, no other text
- Use exact metric and segment names from the available lists
"""
        return prompt
    
    def parse_question(self, question: str) -> Dict[str, Any]:
        system_prompt = self.build_system_prompt()
        full_prompt = f"{system_prompt}\n\nUser question: {question}\n\nResponse (JSON only):"
        
        try:
            response = self.model.generate_content(full_prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            intent = json.loads(response_text)
            return intent
            
        except json.JSONDecodeError as e:
            return {
                "intent": "error",
                "reason": f"Failed to parse LLM response: {e}",
                "raw_response": response_text if 'response_text' in locals() else "No response"
            }
        except Exception as e:
            return {
                "intent": "error",
                "reason": f"LLM error: {str(e)}"
            }


if __name__ == "__main__":
    import os
    from query_generator import QueryGenerator
    import duckdb
    
    print("="*60)
    print("Testing LLM Client with Google AI Studio")
    print("="*60)
    
    api_key = os.environ.get('GOOGLE_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: GOOGLE_API_KEY not set!")
        exit(1)
    
    parser = SemanticLayerParser()
    llm = LLMClient(api_key, parser)
    generator = QueryGenerator(parser)
    
    con = duckdb.connect(':memory:')
    con.execute("CREATE TABLE customers AS SELECT * FROM 'data/marketing_campaign.csv'")
    
    test_questions = [
        "What's average spending for parents?",
        "Show me total spending by age group",
        "Compare CLV for high value vs low value customers",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question}")
        print('='*60)
        
        print("\n1. LLM Understanding:")
        intent = llm.parse_question(question)
        print(f"   Intent: {json.dumps(intent, indent=2)}")
        
        if intent.get('intent') == 'metric_query':
            print("\n2. Generated SQL:")
            filters = None
            if intent.get('segment'):
                filters = {
                    'segment_type': intent.get('segment_type'),
                    'segment': intent.get('segment')
                }
            sql = generator.generate_metric_sql(intent['metric'], filters)
            print(f"   {sql}")
            
            print("\n3. Result:")
            result = con.execute(sql).fetchone()
            print(f"   Answer: ${result[0]:.2f}")
        
        elif intent.get('intent') == 'segment_breakdown':
            print("\n2. Generated SQL:")
            sql = generator.generate_segment_breakdown(
                intent['metric'],
                intent['segment_type']
            )
            print(f"   {sql}")
            
            print("\n3. Results:")
            results = con.execute(sql).df()
            print(results)
        
        elif intent.get('intent') == 'comparison':
            print("\n2. Generated SQL:")
            comp = intent['comparison']
            sql = generator.generate_comparison_query(
                intent['metric'],
                comp['segment_a'],
                comp['segment_b']
            )
            print(f"   {sql}")
            
            print("\n3. Results:")
            results = con.execute(sql).df()
            print(results)
        
        else:
            print(f"\n❌ Intent: {intent}")
    
    print("\n" + "="*60)
    print("✅ LLM Client Working!")
    print("="*60)