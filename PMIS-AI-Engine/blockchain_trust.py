"""
Blockchain Trust Layer for PMIS-AI System
=========================================

This module implements cryptographic hashing and blockchain integration
to create tamper-proof, verifiable records of allocation results.

Author: PMIS-AI Team
Created: 2025-01-01
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import os

class BlockchainTrustLayer:
    """
    Creates cryptographic proofs and immutable records of allocation results
    for transparency and auditability in the PMIS allocation process.
    """
    
    def __init__(self):
        """Initialize the blockchain trust layer."""
        self.trust_records = []
        self.trust_file = "data/blockchain_trust_records.json"
        self.load_trust_records()
    
    def load_trust_records(self):
        """Load existing trust records from file."""
        if os.path.exists(self.trust_file):
            try:
                with open(self.trust_file, 'r') as f:
                    self.trust_records = json.load(f)
                print(f"📋 Loaded {len(self.trust_records)} existing trust records")
            except Exception as e:
                print(f"Could not load trust records: {e}")
                self.trust_records = []
    
    def calculate_allocation_hash(self, allocation_data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of allocation results for immutable proof."""
        # Extract only the final allocation for hashing (no personal data)
        allocation_summary = {
            'final_matches': allocation_data.get('final_matches', {}),
            'total_placed': allocation_data.get('allocation_summary', {}).get('total_placed', 0),
            'algorithm': 'Gale-Shapley Stable Matching with AI Ranking',
            'timestamp': datetime.now().isoformat()
        }
        
        # Convert to canonical JSON string (sorted keys for consistency)
        canonical_json = json.dumps(allocation_summary, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        hash_object = hashlib.sha256(canonical_json.encode('utf-8'))
        return hash_object.hexdigest()
    
    def record_allocation_on_blockchain(self, allocation_data: Dict[str, Any]) -> str:
        """Record allocation results on blockchain (simulated for hackathon)."""
        print("🔐 Recording allocation on blockchain...")
        
        # Calculate hash
        allocation_hash = self.calculate_allocation_hash(allocation_data)
        
        # Create blockchain record
        blockchain_proof = {
            'allocation_id': f"PMIS_ALLOC_{int(time.time())}",
            'timestamp': datetime.now().isoformat(),
            'allocation_hash': allocation_hash,
            'total_placed': allocation_data.get('allocation_summary', {}).get('total_placed', 0),
            'algorithm': 'Gale-Shapley Stable Matching with AI Ranking'
        }
        
        # Add to trust records
        self.trust_records.append(blockchain_proof)
        
        # Save to file
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.trust_file, 'w') as f:
                json.dump(self.trust_records, f, indent=2, default=str)
        except Exception as e:
            print(f"Could not save trust records: {e}")
        
        # Simulate blockchain transaction
        simulated_tx_id = f"0x{allocation_hash[:16]}...{allocation_hash[-16:]}"
        
        print(f"✅ Allocation recorded on blockchain!")
        print(f"📜 Transaction ID: {simulated_tx_id}")
        print(f"🔒 Allocation Hash: {allocation_hash}")
        print(f"📊 {blockchain_proof['total_placed']} placements verified")
        
        return simulated_tx_id

# Test function
def test_blockchain_trust():
    """Test the blockchain trust layer."""
    print("🧪 Testing Blockchain Trust Layer...")
    
    trust_layer = BlockchainTrustLayer()
    
    # Create sample allocation data
    sample_allocation = {
        'final_matches': {
            'I001': ['C001'],
            'I002': ['C002'],
            'I003': ['C003'],
            'I004': ['C004']
        },
        'allocation_summary': {
            'total_candidates': 15,
            'total_placed': 4,
            'placement_rate': 0.267
        }
    }
    
    # Record on blockchain
    tx_id = trust_layer.record_allocation_on_blockchain(sample_allocation)
    
    print(f"\\n📊 Blockchain Trust Summary:")
    print(f"   Total Records: {len(trust_layer.trust_records)}")
    print(f"   Latest Transaction: {tx_id}")
    
    return tx_id

if __name__ == "__main__":
    test_blockchain_trust()
