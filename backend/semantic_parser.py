# backend/semantic_parser.py
"""
Semantic Layer Parser
Reads and parses taxonomy.yml, metadata.yml, and semantic_layer.yml
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class SemanticLayerParser:
    def __init__(self, semantic_dir: str = "semantic"):
        self.semantic_dir = Path(semantic_dir)
        self.taxonomy = None
        self.metadata = None
        self.metrics = None
        
        # Load all YAML files on init
        self.load_all()
    
    def load_yaml(self, filename: str) -> Dict[Any, Any]:
        """Load a YAML file and return parsed content"""
        filepath = self.semantic_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def load_all(self):
        """Load all semantic layer files"""
        print("Loading semantic layer files...")
        
        self.taxonomy = self.load_yaml('taxonomy.yml')
        print("✅ Loaded taxonomy.yml")
        
        self.metadata = self.load_yaml('metadata.yml')
        print("✅ Loaded metadata.yml")
        
        self.metrics = self.load_yaml('semantic_layer.yml')
        print("✅ Loaded semantic_layer.yml")
    
    def get_customer_segment(self, segment_type: str, segment_name: str) -> Optional[Dict]:
        """
        Get a customer segment definition
        
        Args:
            segment_type: e.g., 'customer_age_segments', 'family_status', 'value_tiers'
            segment_name: e.g., 'young_adult', 'parents', 'high_value'
        
        Returns:
            Dictionary with segment definition or None
        """
        taxonomy = self.taxonomy.get('taxonomy', {})
        segments = taxonomy.get(segment_type, {})
        
        if segment_name in segments:
            return segments[segment_name]
        
        return None
    
    def get_metric(self, metric_name: str) -> Optional[Dict]:
        """
        Get a metric definition
        
        Args:
            metric_name: e.g., 'total_spending', 'customer_lifetime_value'
        
        Returns:
            Dictionary with metric definition or None
        """
        metrics_list = self.metrics.get('metrics', [])
        
        for metric in metrics_list:
            if metric.get('name') == metric_name:
                return metric
        
        return None
    
    def get_column_metadata(self, column_name: str) -> Optional[Dict]:
        """
        Get metadata for a specific column
        
        Args:
            column_name: e.g., 'Income', 'MntWines'
        
        Returns:
            Dictionary with column metadata or None
        """
        columns = self.metadata.get('columns', {})
        return columns.get(column_name)
    
    def list_all_segments(self) -> Dict[str, list]:
        """List all available customer segments"""
        taxonomy = self.taxonomy.get('taxonomy', {})
        
        result = {}
        for segment_type, segments in taxonomy.items():
            if isinstance(segments, dict) and segment_type not in ['metadata']:
                result[segment_type] = list(segments.keys())
        
        return result
    
    def list_all_metrics(self) -> list:
        """List all available metrics"""
        metrics_list = self.metrics.get('metrics', [])
        return [m['name'] for m in metrics_list if 'name' in m]


# Test the parser
if __name__ == "__main__":
    print("="*60)
    print("Testing Semantic Layer Parser")
    print("="*60)
    
    # Initialize parser
    parser = SemanticLayerParser()
    
    # Test 1: List all segments
    print("\n1. Available Customer Segments:")
    segments = parser.list_all_segments()
    for seg_type, seg_names in segments.items():
        print(f"\n  {seg_type}:")
        for name in seg_names:
            print(f"    - {name}")
    
    # Test 2: Get specific segment
    print("\n2. Get 'parents' segment:")
    parents = parser.get_customer_segment('family_status', 'parents')
    if parents:
        print(f"   Definition: {parents.get('definition')}")
        print(f"   Label: {parents.get('label')}")
        print(f"   Description: {parents.get('description')}")
    
    # Test 3: List all metrics
    print("\n3. Available Metrics:")
    metrics = parser.list_all_metrics()
    for metric in metrics:
        print(f"   - {metric}")
    
    # Test 4: Get specific metric
    print("\n4. Get 'total_spending' metric:")
    total_spending = parser.get_metric('total_spending')
    if total_spending:
        print(f"   Label: {total_spending.get('label')}")
        print(f"   Type: {total_spending.get('type')}")
        print(f"   SQL: {total_spending.get('sql')}")
    
    # Test 5: Get column metadata
    print("\n5. Get 'Income' column metadata:")
    income_meta = parser.get_column_metadata('Income')
    if income_meta:
        print(f"   Display Name: {income_meta.get('display_name')}")
        print(f"   Description: {income_meta.get('description')}")
        print(f"   PII Level: {income_meta.get('pii_level')}")
    
    print("\n" + "="*60)
    print("✅ Semantic Layer Parser Working!")
    print("="*60)