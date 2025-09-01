"""
Blockchain Trust Layer for PMIS-AI Engine
Implements cryptographic hash generation and verification for tamper-proof results
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any, List

class BlockchainTrustLayer:
    def __init__(self):
        self.hash_algorithm = 'sha256'
        self.verification_records = []
    
    def generate_allocation_hash(self, allocation_data: Dict) -> Dict:
        """
        Generate cryptographic hash of allocation results
        
        Args:
            allocation_data: Complete allocation results
            
        Returns:
            Dict: Hash verification data
        """
        try:
            # Prepare data for hashing (exclude sensitive personal info)
            hash_payload = {
                'matches': allocation_data.get('matches', {}),
                'quota_stats': allocation_data.get('quota_stats', {}),
                'total_matches': len(allocation_data.get('matches', {})),
                'algorithm_iterations': allocation_data.get('iterations', 0),
                'is_stable': allocation_data.get('is_stable', False),
                'timestamp': allocation_data.get('timestamp', datetime.now().isoformat()),
                'system_version': 'PMIS-AI-v1.0'
            }
            
            # Convert to canonical JSON string
            canonical_json = json.dumps(hash_payload, sort_keys=True, separators=(',', ':'))
            
            # Generate SHA-256 hash
            hash_bytes = canonical_json.encode('utf-8')
            allocation_hash = hashlib.sha256(hash_bytes).hexdigest()
            
            # Create verification record
            verification_record = {
                'hash': allocation_hash,
                'algorithm': self.hash_algorithm,
                'timestamp': datetime.now().isoformat(),
                'data_summary': {
                    'total_matches': hash_payload['total_matches'],
                    'rural_percentage': hash_payload['quota_stats'].get('rural_percentage', 0),
                    'stability_verified': hash_payload['is_stable']
                },
                'hash_payload': hash_payload
            }
            
            # Store verification record
            self.verification_records.append(verification_record)
            
            return {
                'success': True,
                'hash': allocation_hash,
                'verification_record': verification_record,
                'message': 'Allocation hash generated successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate hash: {str(e)}',
                'hash': None
            }
    
    def verify_allocation_integrity(self, allocation_data: Dict, provided_hash: str) -> Dict:
        """
        Verify the integrity of allocation data against provided hash
        
        Args:
            allocation_data: Allocation data to verify
            provided_hash: Hash to verify against
            
        Returns:
            Dict: Verification result
        """
        try:
            # Generate hash from current data
            hash_result = self.generate_allocation_hash(allocation_data)
            
            if not hash_result['success']:
                return {
                    'verified': False,
                    'error': 'Failed to generate verification hash',
                    'details': hash_result['error']
                }
            
            computed_hash = hash_result['hash']
            
            # Compare hashes
            is_verified = computed_hash == provided_hash
            
            return {
                'verified': is_verified,
                'computed_hash': computed_hash,
                'provided_hash': provided_hash,
                'timestamp': datetime.now().isoformat(),
                'message': 'Integrity verified' if is_verified else 'Hash mismatch detected'
            }
            
        except Exception as e:
            return {
                'verified': False,
                'error': f'Verification failed: {str(e)}'
            }
    
    def create_audit_trail(self, allocation_results: Dict, candidates: List[Dict], 
                          internships: List[Dict]) -> Dict:
        """
        Create comprehensive audit trail for transparency
        
        Args:
            allocation_results: Final allocation results
            candidates: List of all candidates
            internships: List of all internships
            
        Returns:
            Dict: Audit trail data
        """
        try:
            # Generate allocation hash
            hash_result = self.generate_allocation_hash(allocation_results)
            
            if not hash_result['success']:
                return {
                    'success': False,
                    'error': 'Failed to create audit trail'
                }
            
            # Create audit summary
            audit_data = {
                'audit_id': f"PMIS-AI-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'system_info': {
                    'version': 'PMIS-AI-v1.0',
                    'algorithm': 'Gale-Shapley Stable Matching',
                    'hash_algorithm': self.hash_algorithm
                },
                'input_summary': {
                    'total_candidates': len(candidates),
                    'total_internships': len(internships),
                    'total_capacity': sum(i.get('capacity', 0) for i in internships)
                },
                'allocation_summary': {
                    'total_matches': len(allocation_results.get('matches', {})),
                    'quota_compliance': allocation_results.get('quota_stats', {}),
                    'algorithm_iterations': allocation_results.get('iterations', 0),
                    'stability_verified': allocation_results.get('is_stable', False)
                },
                'blockchain_verification': hash_result['verification_record'],
                'compliance_metrics': self._calculate_compliance_metrics(
                    allocation_results, candidates, internships
                )
            }
            
            return {
                'success': True,
                'audit_trail': audit_data,
                'blockchain_hash': hash_result['hash']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Audit trail creation failed: {str(e)}'
            }
    
    def _calculate_compliance_metrics(self, allocation_results: Dict, 
                                    candidates: List[Dict], internships: List[Dict]) -> Dict:
        """Calculate detailed compliance metrics"""
        try:
            matches = allocation_results.get('matches', {})
            candidate_lookup = {c['candidate_id']: c for c in candidates}
            
            # Category-wise analysis
            category_stats = {}
            rural_stats = {'rural': 0, 'urban': 0}
            age_distribution = {}
            
            for candidate_id in matches.keys():
                candidate = candidate_lookup.get(candidate_id)
                if candidate:
                    # Social category
                    category = candidate.get('social_category', 'General')
                    category_stats[category] = category_stats.get(category, 0) + 1
                    
                    # Rural/Urban
                    if candidate.get('is_rural', False):
                        rural_stats['rural'] += 1
                    else:
                        rural_stats['urban'] += 1
                    
                    # Age distribution
                    age = candidate.get('age', 0)
                    age_distribution[age] = age_distribution.get(age, 0) + 1
            
            total_allocated = len(matches)
            
            return {
                'total_allocated': total_allocated,
                'category_distribution': category_stats,
                'rural_urban_split': rural_stats,
                'rural_percentage': (rural_stats['rural'] / total_allocated * 100) if total_allocated > 0 else 0,
                'age_distribution': age_distribution,
                'quota_compliance': {
                    'rural_quota_met': (rural_stats['rural'] / total_allocated * 100) >= 30 if total_allocated > 0 else False,
                    'target_rural_percentage': 30.0,
                    'actual_rural_percentage': (rural_stats['rural'] / total_allocated * 100) if total_allocated > 0 else 0
                }
            }
            
        except Exception as e:
            return {'error': f'Compliance calculation failed: {str(e)}'}
    
    def export_verification_data(self, output_file: str = None) -> str:
        """
        Export all verification records to JSON file
        
        Args:
            output_file: Optional output filename
            
        Returns:
            str: Output filename
        """
        try:
            if not output_file:
                output_file = f"blockchain_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'system_info': {
                    'version': 'PMIS-AI-v1.0',
                    'hash_algorithm': self.hash_algorithm
                },
                'verification_records': self.verification_records,
                'total_records': len(self.verification_records)
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Verification data exported to {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Export failed: {str(e)}")
            return ""
    
    def simulate_blockchain_storage(self, hash_data: str) -> Dict:
        """
        Simulate blockchain storage (for demonstration)
        In production, this would interact with actual blockchain networks
        
        Args:
            hash_data: Hash to store on blockchain
            
        Returns:
            Dict: Simulated blockchain transaction data
        """
        # Simulate blockchain transaction
        transaction_data = {
            'transaction_id': f"0x{hashlib.md5(hash_data.encode()).hexdigest()}",
            'block_number': 12345678,  # Simulated block number
            'network': 'Ethereum Sepolia Testnet',  # Test network
            'gas_used': 21000,  # Simulated gas usage
            'timestamp': datetime.now().isoformat(),
            'hash_stored': hash_data,
            'status': 'confirmed',
            'confirmation_blocks': 12
        }
        
        return {
            'success': True,
            'message': 'Hash successfully stored on blockchain (simulated)',
            'transaction': transaction_data
        }


# Test function
if __name__ == "__main__":
    print("=== Testing Blockchain Trust Layer ===")
    
    blockchain = BlockchainTrustLayer()
    
    # Test data
    test_allocation = {
        'matches': {1: 1, 2: 2, 3: 1},
        'quota_stats': {
            'rural_percentage': 33.3,
            'total_allocated': 3,
            'category_distribution': {'General': 2, 'SC': 1}
        },
        'iterations': 5,
        'is_stable': True,
        'timestamp': datetime.now().isoformat()
    }
    
    # Generate hash
    hash_result = blockchain.generate_allocation_hash(test_allocation)
    print(f"Hash Generation: {'✅ Success' if hash_result['success'] else '❌ Failed'}")
    
    if hash_result['success']:
        print(f"Generated Hash: {hash_result['hash']}")
        
        # Verify integrity
        verification = blockchain.verify_allocation_integrity(test_allocation, hash_result['hash'])
        print(f"Integrity Verification: {'✅ Verified' if verification['verified'] else '❌ Failed'}")
        
        # Simulate blockchain storage
        blockchain_result = blockchain.simulate_blockchain_storage(hash_result['hash'])
        print(f"Blockchain Storage: {'✅ Success' if blockchain_result['success'] else '❌ Failed'}")
        
        # Export verification data
        export_file = blockchain.export_verification_data()
        print(f"Export: {'✅ Success' if export_file else '❌ Failed'}")
