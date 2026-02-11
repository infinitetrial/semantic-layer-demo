# backend/query_generator.py
"""
Query Generator
Takes semantic layer definitions and generates SQL for DuckDB

This module converts semantic layer definitions (from YAML files) into
executable SQL queries. It handles:
- Metric calculations with proper business logic
- Segment filtering using taxonomy definitions
- Comparisons across different customer segments
- Consistent SQL generation for repeatable results
"""

from semantic_parser import SemanticLayerParser
from typing import Dict, Any, Optional, List

class QueryGenerator:
    """
    Generates SQL queries from semantic layer definitions
    
    Uses the SemanticLayerParser to read taxonomy, metadata, and metric
    definitions, then constructs valid SQL queries that enforce business
    logic and ensure consistency.
    """
    
    def __init__(self, semantic_parser: SemanticLayerParser):
        """
        Initialize the query generator
        
        Args:
            semantic_parser: Instance of SemanticLayerParser with loaded YAML files
        """
        self.parser = semantic_parser
    
    def generate_metric_sql(self, metric_name: str, filters: Optional[Dict] = None) -> str:
        """
        Generate SQL for a metric with optional filters
        
        Args:
            metric_name: Name of metric (e.g., 'total_spending')
            filters: Optional filters like {'segment': 'parents', 'segment_type': 'family_status'}
        
        Returns:
            SQL query string
        """
        # Get metric definition
        metric = self.parser.get_metric(metric_name)
        if not metric:
            raise ValueError(f"Metric '{metric_name}' not found in semantic layer")
        
        # Get metric SQL
        metric_sql = metric.get('sql', '').strip()
        
        # Build WHERE clause from filters
        where_clauses = []
        
        if filters:
            segment_type = filters.get('segment_type')
            segment_name = filters.get('segment')
            
            if segment_type and segment_name:
                segment = self.parser.get_customer_segment(segment_type, segment_name)
                if segment:
                    segment_definition = segment.get('definition')
                    where_clauses.append(f"({segment_definition})")
        
        # Build complete query
        if metric.get('type') == 'sum' or metric.get('type') == 'calculated':
            # Aggregate query
            select_clause = f"AVG({metric_sql}) as value"
            
            query = f"""
            SELECT 
                {select_clause}
            FROM customers
            """
            
            if where_clauses:
                query += f"\nWHERE {' AND '.join(where_clauses)}"
            
            # Filter out nulls for income-dependent metrics
            if 'Income' in metric_sql:
                if where_clauses:
                    query += "\n  AND Income IS NOT NULL"
                else:
                    query += "\nWHERE Income IS NOT NULL"
        
        else:
            # Other types
            query = f"SELECT {metric_sql} FROM customers"
        
        return query.strip()
    
    def generate_segment_breakdown(self, metric_name: str, segment_type: str) -> str:
        """
        Generate SQL to show metric broken down by segment
        
        Args:
            metric_name: Name of metric
            segment_type: Type of segment (e.g., 'customer_age_segments', 'family_status')
        
        Returns:
            SQL query string
        """
        # Get metric
        metric = self.parser.get_metric(metric_name)
        if not metric:
            raise ValueError(f"Metric '{metric_name}' not found")
        
        metric_sql = metric.get('sql', '').strip()
        
        # Get all segments of this type
        taxonomy = self.parser.taxonomy.get('taxonomy', {})
        segments = taxonomy.get(segment_type, {})
        
        # Build CASE statement for segments
        case_clauses = []
        for seg_name, seg_def in segments.items():
            if isinstance(seg_def, dict):
                definition = seg_def.get('definition')
                label = seg_def.get('label', seg_name)
                if definition:
                    case_clauses.append(f"WHEN {definition} THEN '{label}'")
        
        case_statement = "CASE\n    " + "\n    ".join(case_clauses) + "\n    ELSE 'Other'\nEND"
        
        # Build query
        query = f"""
        SELECT 
            {case_statement} as segment,
            COUNT(*) as customer_count,
            ROUND(AVG({metric_sql}), 2) as avg_value
        FROM customers
        WHERE Income IS NOT NULL
        GROUP BY segment
        ORDER BY avg_value DESC
        """
        
        return query.strip()
    
    def generate_comparison_query(self, metric_name: str, segment_a: Dict, segment_b: Dict) -> str:
        """
        Generate SQL to compare metric across two segments
        
        Args:
            metric_name: Name of metric
            segment_a: {'type': 'family_status', 'name': 'parents'}
            segment_b: {'type': 'family_status', 'name': 'no_children'}
        
        Returns:
            SQL query string
        """
        metric = self.parser.get_metric(metric_name)
        if not metric:
            raise ValueError(f"Metric '{metric_name}' not found")
        
        metric_sql = metric.get('sql', '').strip()
        
        # Get segment definitions
        seg_a = self.parser.get_customer_segment(segment_a['type'], segment_a['name'])
        seg_b = self.parser.get_customer_segment(segment_b['type'], segment_b['name'])
        
        if not seg_a or not seg_b:
            raise ValueError("Segment not found")
        
        query = f"""
        SELECT 
            '{seg_a.get("label")}' as segment,
            COUNT(*) as customers,
            ROUND(AVG({metric_sql}), 2) as avg_value
        FROM customers
        WHERE ({seg_a.get('definition')})
          AND Income IS NOT NULL
        
        UNION ALL
        
        SELECT 
            '{seg_b.get("label")}' as segment,
            COUNT(*) as customers,
            ROUND(AVG({metric_sql}), 2) as avg_value
        FROM customers
        WHERE ({seg_b.get('definition')})
          AND Income IS NOT NULL
        """
        
        return query.strip()


# Test the query generator
if __name__ == "__main__":
    import duckdb
    
    print("="*60)
    print("Testing Query Generator")
    print("="*60)
    
    # Initialize
    parser = SemanticLayerParser()
    generator = QueryGenerator(parser)
    
    # Connect to DuckDB
    con = duckdb.connect(':memory:')
    con.execute("CREATE TABLE customers AS SELECT * FROM 'data/marketing_campaign.csv'")
    
    # Test 1: Simple metric query
    print("\n1. Average total spending for ALL customers:")
    sql = generator.generate_metric_sql('total_spending')
    print(f"\nGenerated SQL:\n{sql}\n")
    result = con.execute(sql).fetchone()
    print(f"Result: ${result[0]:.2f}")
    
    # Test 2: Metric with segment filter
    print("\n" + "="*60)
    print("2. Average total spending for PARENTS:")
    sql = generator.generate_metric_sql(
        'total_spending', 
        filters={'segment_type': 'family_status', 'segment': 'parents'}
    )
    print(f"\nGenerated SQL:\n{sql}\n")
    result = con.execute(sql).fetchone()
    print(f"Result: ${result[0]:.2f}")
    
    # Test 3: Segment breakdown
    print("\n" + "="*60)
    print("3. Total spending by age segment:")
    sql = generator.generate_segment_breakdown('total_spending', 'customer_age_segments')
    print(f"\nGenerated SQL:\n{sql}\n")
    results = con.execute(sql).df()
    print(results)
    
    # Test 4: Comparison
    print("\n" + "="*60)
    print("4. Compare CLV: Parents vs No Children:")
    sql = generator.generate_comparison_query(
        'customer_lifetime_value',
        {'type': 'family_status', 'name': 'parents'},
        {'type': 'family_status', 'name': 'no_children'}
    )
    print(f"\nGenerated SQL:\n{sql}\n")
    results = con.execute(sql).df()
    print(results)
    
    print("\n" + "="*60)
    print("✅ Query Generator Working!")
    print("="*60)