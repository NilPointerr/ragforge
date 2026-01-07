import logging
import json
from typing import List, Dict, Any, Optional, Set
from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError

from ragforge.settings import settings
from ragforge.llm import get_default_llm
from ragforge.errors import GraphError, ConfigurationError

logger = logging.getLogger(__name__)

class GraphStore:
    """
    Manages the Neo4j knowledge graph for GraphRAG functionality.
    
    This class handles:
    - Neo4j connection management
    - Entity extraction from documents
    - Relationship extraction
    - Graph construction and querying
    - Hybrid retrieval (graph + vector)
    """
    
    def __init__(self):
        """
        Initialize the Neo4j graph store client.
        """
        if not settings.enable_graphrag:
            logger.info("GraphRAG is disabled. Skipping Neo4j initialization.")
            self.driver = None
            return
            
        if not settings.neo4j_password:
            raise ConfigurationError(
                "NEO4J_PASSWORD environment variable is not set. "
                "Please set RAGFORGE_NEO4J_PASSWORD to use GraphRAG functionality."
            )
        
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            # Verify connection
            self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j at {settings.neo4j_uri}")
            
            # Initialize schema
            self._initialize_schema()
            
        except ServiceUnavailable as e:
            raise GraphError(
                f"Could not connect to Neo4j at {settings.neo4j_uri}. "
                f"Make sure Neo4j is running. Error: {e}"
            )
        except AuthError as e:
            raise GraphError(
                f"Neo4j authentication failed. Check your credentials. Error: {e}"
            )
        except Exception as e:
            raise GraphError(f"Failed to initialize Neo4j client: {e}")
    
    def _initialize_schema(self):
        """
        Initialize the graph schema with constraints and indexes.
        """
        if not self.driver:
            return
            
        with self.driver.session(database=settings.neo4j_database) as session:
            # Create constraints for uniqueness
            session.run("""
                CREATE CONSTRAINT entity_id IF NOT EXISTS
                FOR (e:Entity) REQUIRE e.id IS UNIQUE
            """)
            
            # Create indexes for better query performance
            session.run("""
                CREATE INDEX entity_name IF NOT EXISTS
                FOR (e:Entity) ON (e.name)
            """)
            
            session.run("""
                CREATE INDEX entity_type IF NOT EXISTS
                FOR (e:Entity) ON (e.type)
            """)
            
            logger.info("Neo4j schema initialized")
    
    def extract_entities_and_relationships(self, text: str) -> Dict[str, Any]:
        """
        Extract entities and relationships from text using LLM.
        
        Args:
            text: The text to extract entities and relationships from.
            
        Returns:
            Dictionary with 'entities' and 'relationships' keys.
        """
        if not self.driver:
            return {"entities": [], "relationships": []}
        
        llm = get_default_llm()
        
        extraction_prompt = f"""Extract entities and relationships from the following text.

Text:
{text}

Extract:
1. Entities: People, places, organizations, concepts, objects mentioned
2. Relationships: How these entities relate to each other

Return a JSON object with this structure:
{{
    "entities": [
        {{"name": "Entity Name", "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT|OTHER"}},
        ...
    ],
    "relationships": [
        {{"source": "Entity1", "target": "Entity2", "type": "RELATIONSHIP_TYPE", "description": "brief description"}},
        ...
    ]
}}

Only extract entities and relationships that are explicitly mentioned in the text.
Be concise and accurate."""

        system_prompt = """You are an expert at extracting structured information from text.
Return only valid JSON. Do not include any explanations or markdown formatting."""

        try:
            response = llm.generate_response(extraction_prompt, system_prompt)
            
            # Clean JSON response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            result = json.loads(cleaned)
            
            # Validate structure
            if "entities" not in result:
                result["entities"] = []
            if "relationships" not in result:
                result["relationships"] = []
                
            return result
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse entity extraction response: {e}")
            return {"entities": [], "relationships": []}
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {"entities": [], "relationships": []}
    
    def add_document_to_graph(self, text: str, doc_id: Optional[str] = None) -> None:
        """
        Add a document to the knowledge graph by extracting and storing entities and relationships.
        
        Args:
            text: The document text to process.
            doc_id: Optional document identifier.
        """
        if not self.driver:
            return
        
        try:
            # Extract entities and relationships
            extracted = self.extract_entities_and_relationships(text)
            entities = extracted.get("entities", [])
            relationships = extracted.get("relationships", [])
            
            if not entities and not relationships:
                logger.debug(f"No entities or relationships extracted from document")
                return
            
            with self.driver.session(database=settings.neo4j_database) as session:
                # Create or update entities
                for entity in entities:
                    entity_name = entity.get("name", "").strip()
                    entity_type = entity.get("type", "OTHER").upper()
                    
                    if not entity_name:
                        continue
                    
                    # Create unique ID for entity
                    entity_id = f"{entity_type}:{entity_name}"
                    
                    session.run("""
                        MERGE (e:Entity {id: $entity_id})
                        SET e.name = $name,
                            e.type = $type,
                            e.last_seen = timestamp()
                        ON CREATE SET e.created = timestamp()
                    """, {
                        "entity_id": entity_id,
                        "name": entity_name,
                        "type": entity_type
                    })
                
                # Create relationships
                for rel in relationships:
                    source_name = rel.get("source", "").strip()
                    target_name = rel.get("target", "").strip()
                    rel_type = rel.get("type", "RELATED_TO").upper().replace(" ", "_")
                    description = rel.get("description", "").strip()
                    
                    if not source_name or not target_name:
                        continue
                    
                    # Find actual entity IDs by name
                    source_result = session.run("""
                        MATCH (e:Entity {name: $name})
                        RETURN e.id as id
                        LIMIT 1
                    """, {"name": source_name})
                    
                    source_record = source_result.single()
                    if not source_record:
                        continue  # Skip if source entity doesn't exist
                    source_id = source_record["id"]
                    
                    target_result = session.run("""
                        MATCH (e:Entity {name: $name})
                        RETURN e.id as id
                        LIMIT 1
                    """, {"name": target_name})
                    
                    target_record = target_result.single()
                    if not target_record:
                        continue  # Skip if target entity doesn't exist
                    target_id = target_record["id"]
                    
                    # Create relationship
                    session.run("""
                        MATCH (source:Entity {id: $source_id})
                        MATCH (target:Entity {id: $target_id})
                        MERGE (source)-[r:RELATES_TO {type: $rel_type}]->(target)
                        SET r.description = $description,
                            r.last_seen = timestamp()
                        ON CREATE SET r.created = timestamp()
                    """, {
                        "source_id": source_id,
                        "target_id": target_id,
                        "rel_type": rel_type,
                        "description": description
                    })
                
                logger.info(f"Added {len(entities)} entities and {len(relationships)} relationships to graph")
                
        except Exception as e:
            logger.error(f"Error adding document to graph: {e}")
            raise GraphError(f"Failed to add document to graph: {e}")
    
    def query_related_entities(self, query_text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query the graph for entities related to the query text.
        Uses entity extraction to find relevant entities, then traverses the graph.
        
        Args:
            query_text: The query text to search for.
            limit: Maximum number of results to return.
            
        Returns:
            List of dictionaries containing entity information and context.
        """
        if not self.driver:
            return []
        
        try:
            # Extract entities from query
            extracted = self.extract_entities_and_relationships(query_text)
            query_entities = [e.get("name", "").strip() for e in extracted.get("entities", [])]
            
            if not query_entities:
                # Fallback: search by text similarity in entity names
                query_entities = [query_text]
            
            results = []
            
            with self.driver.session(database=settings.neo4j_database) as session:
                for entity_name in query_entities[:3]:  # Limit to top 3 entities
                    # Find matching entities and their neighbors
                    query = """
                        MATCH (e:Entity)
                        WHERE toLower(e.name) CONTAINS toLower($entity_name)
                        OPTIONAL MATCH (e)-[r:RELATES_TO]-(related:Entity)
                        RETURN e.name as entity_name,
                               e.type as entity_type,
                               collect(DISTINCT {
                                   related: related.name,
                                   relation: r.type,
                                   description: r.description
                               }) as relationships
                        LIMIT $limit
                    """
                    
                    result = session.run(query, {
                        "entity_name": entity_name,
                        "limit": limit
                    })
                    
                    for record in result:
                        entity_info = {
                            "entity": record["entity_name"],
                            "type": record["entity_type"],
                            "relationships": record["relationships"]
                        }
                        results.append(entity_info)
            
            # Deduplicate
            seen = set()
            unique_results = []
            for r in results:
                key = (r["entity"], r["type"])
                if key not in seen:
                    seen.add(key)
                    unique_results.append(r)
            
            return unique_results[:limit]
            
        except Exception as e:
            logger.error(f"Error querying graph: {e}")
            return []
    
    def get_graph_context(self, query_text: str, max_entities: int = 5) -> str:
        """
        Get graph-based context for a query by finding related entities and their connections.
        
        Args:
            query_text: The query text.
            max_entities: Maximum number of entities to include.
            
        Returns:
            A formatted string containing graph context.
        """
        if not self.driver:
            return ""
        
        related_entities = self.query_related_entities(query_text, limit=max_entities)
        
        if not related_entities:
            return ""
        
        context_parts = ["Graph Context:"]
        
        for entity_info in related_entities:
            entity_name = entity_info["entity"]
            entity_type = entity_info["type"]
            relationships = entity_info["relationships"]
            
            context_parts.append(f"\n{entity_name} ({entity_type}):")
            
            for rel in relationships[:3]:  # Limit relationships per entity
                related = rel.get("related", "")
                rel_type = rel.get("relation", "")
                desc = rel.get("description", "")
                
                if related:
                    context_parts.append(f"  - {rel_type}: {related}")
                    if desc:
                        context_parts.append(f"    ({desc})")
        
        return "\n".join(context_parts)
    
    def clear_graph(self) -> None:
        """
        Clear all nodes and relationships from the graph.
        Use with caution!
        """
        if not self.driver:
            return
        
        try:
            with self.driver.session(database=settings.neo4j_database) as session:
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Graph cleared")
        except Exception as e:
            logger.error(f"Error clearing graph: {e}")
            raise GraphError(f"Failed to clear graph: {e}")
    
    def close(self):
        """Close the Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
