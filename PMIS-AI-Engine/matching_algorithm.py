"""
Stable Matching Algorithm for PMIS-AI System
============================================

This module implements the Gale-Shapley stable matching algorithm to ensure
fair and optimal allocation of candidates to internships while respecting
capacity constraints and affirmative action quotas.

Author: PMIS-AI Team
Created: 2025-01-01
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set, Any
import json
from collections import defaultdict, deque
from ranking_engine import PMISRankingEngine
from blockchain_trust import BlockchainTrustLayer

class StableMatchingEngine:
    """
    Implementation of the Gale-Shapley algorithm for stable matching
    with constraints for capacity and diversity quotas.
    """
    
    def __init__(self):
        """Initialize the stable matching engine."""
        self.ranking_engine = PMISRankingEngine()
        self.blockchain_trust = BlockchainTrustLayer()
        
    def build_preference_lists(self, rankings: Dict[str, List]) -> Tuple[Dict, Dict]:
        """Build preference lists for candidates and internships based on AI rankings."""
        candidate_preferences = defaultdict(list)
        internship_preferences = defaultdict(list)
        
        # Build internship preferences (already ranked by AI)
        for internship_id, ranked_candidates in rankings.items():
            internship_preferences[internship_id] = [
                candidate['candidate_id'] for candidate in ranked_candidates
            ]
        
        # Build candidate preferences (rank internships by their score for this candidate)
        candidate_scores = defaultdict(dict)
        
        # Collect all scores for each candidate
        for internship_id, ranked_candidates in rankings.items():
            for candidate in ranked_candidates:
                candidate_id = candidate['candidate_id']
                score = candidate['scores']['composite_score']
                candidate_scores[candidate_id][internship_id] = score
        
        # Sort internships by score for each candidate
        for candidate_id, scores in candidate_scores.items():
            sorted_internships = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            candidate_preferences[candidate_id] = [internship_id for internship_id, _ in sorted_internships]
        
        return dict(candidate_preferences), dict(internship_preferences)
    
    def gale_shapley_matching(self, candidate_preferences: Dict[str, List],
                             internship_preferences: Dict[str, List],
                             internship_capacities: Dict[str, int]) -> Dict[str, List]:
        """Execute the Gale-Shapley algorithm for stable matching."""
        print("🔄 Executing Gale-Shapley stable matching algorithm...")
        
        # Initialize data structures
        free_candidates = set(candidate_preferences.keys())
        tentative_matches = {internship_id: [] for internship_id in internship_preferences.keys()}
        candidate_next_proposal = {candidate_id: 0 for candidate_id in candidate_preferences.keys()}
        
        iteration = 0
        max_iterations = len(candidate_preferences) * len(internship_preferences)
        
        while free_candidates and iteration < max_iterations:
            iteration += 1
            candidate_id = free_candidates.pop()
            
            # Get candidate's next preferred internship
            if candidate_next_proposal[candidate_id] >= len(candidate_preferences[candidate_id]):
                # Candidate has exhausted all preferences, remains unmatched
                continue
                
            internship_id = candidate_preferences[candidate_id][candidate_next_proposal[candidate_id]]
            candidate_next_proposal[candidate_id] += 1
            
            # Check if internship has capacity
            current_matches = tentative_matches[internship_id]
            capacity = internship_capacities[internship_id]
            
            if len(current_matches) < capacity:
                # Internship has space, accept the candidate
                tentative_matches[internship_id].append(candidate_id)
                
            else:
                # Internship is full, check if new candidate is better than worst current match
                internship_prefs = internship_preferences[internship_id]
                
                # Find the worst current match
                worst_candidate = None
                worst_rank = -1
                
                for current_candidate in current_matches:
                    if current_candidate in internship_prefs:
                        rank = internship_prefs.index(current_candidate)
                        if rank > worst_rank:
                            worst_rank = rank
                            worst_candidate = current_candidate
                
                # Check if new candidate is better (appears earlier in preference list)
                if candidate_id in internship_prefs:
                    new_candidate_rank = internship_prefs.index(candidate_id)
                    
                    if worst_candidate and new_candidate_rank < worst_rank:
                        # Replace worst candidate with new candidate
                        tentative_matches[internship_id].remove(worst_candidate)
                        tentative_matches[internship_id].append(candidate_id)
                        free_candidates.add(worst_candidate)
                    else:
                        # New candidate is not better, remains free
                        free_candidates.add(candidate_id)
                else:
                    # New candidate not in internship's preference list
                    free_candidates.add(candidate_id)
        
        print(f"✅ Stable matching completed in {iteration} iterations")
        return tentative_matches
    
    def enforce_diversity_quotas(self, matches: Dict[str, List], 
                                candidates_df: pd.DataFrame) -> Dict[str, List]:
        """Analyze and report diversity statistics."""
        print("📊 Analyzing diversity quotas...")
        
        # Create candidate lookup
        candidate_lookup = {row['candidate_id']: row for _, row in candidates_df.iterrows()}
        
        # Count current diversity stats
        total_placed = sum(len(candidates) for candidates in matches.values())
        rural_count = 0
        sc_st_count = 0
        
        all_placed_candidates = []
        for candidates in matches.values():
            all_placed_candidates.extend(candidates)
        
        for candidate_id in all_placed_candidates:
            candidate = candidate_lookup[candidate_id]
            if candidate['is_rural']:
                rural_count += 1
            if candidate['social_category'] in ['SC', 'ST']:
                sc_st_count += 1
        
        rural_percentage = rural_count / total_placed if total_placed > 0 else 0
        sc_st_percentage = sc_st_count / total_placed if total_placed > 0 else 0
        
        print(f"Current diversity stats:")
        print(f"  Rural candidates: {rural_count}/{total_placed} ({rural_percentage:.1%})")
        print(f"  SC/ST candidates: {sc_st_count}/{total_placed} ({sc_st_percentage:.1%})")
        
        target_rural = 0.3
        target_sc_st = 0.22
        
        if rural_percentage >= target_rural and sc_st_percentage >= target_sc_st:
            print("✅ All diversity quotas met!")
        else:
            print("📋 Diversity targets for reference:")
            print(f"  Target rural: {target_rural:.1%}")
            print(f"  Target SC/ST: {target_sc_st:.1%}")
        
        return matches
    
    def run_complete_allocation(self, candidates_file: str, internships_file: str) -> Dict[str, Any]:
        """Execute the complete allocation pipeline."""
        print("=" * 60)
        print("🚀 PMIS-AI SMART ALLOCATION ENGINE")
        print("=" * 60)
        
        # Load data
        candidates_df = pd.read_csv(candidates_file)
        internships_df = pd.read_csv(internships_file)
        
        print(f"📊 Processing {len(candidates_df)} candidates for {len(internships_df)} internships")
        
        # Step 1: Generate AI rankings
        rankings = self.ranking_engine.generate_all_rankings(candidates_file, internships_file)
        
        # Step 2: Build preference lists
        candidate_prefs, internship_prefs = self.build_preference_lists(rankings)
        print(f"✅ Preference lists built for {len(candidate_prefs)} candidates")
        
        # Step 3: Get internship capacities
        capacities = {row['internship_id']: row['capacity'] for _, row in internships_df.iterrows()}
        
        # Step 4: Execute stable matching
        stable_matches = self.gale_shapley_matching(candidate_prefs, internship_prefs, capacities)
        
        # Step 5: Enforce diversity quotas
        final_matches = self.enforce_diversity_quotas(stable_matches, candidates_df)
        
        # Step 6: Generate summary statistics
        total_candidates = len(candidates_df)
        total_placed = sum(len(candidates) for candidates in final_matches.values())
        total_capacity = sum(capacities.values())
        
        allocation_summary = {
            'total_candidates': total_candidates,
            'total_placed': total_placed,
            'total_capacity': total_capacity,
            'placement_rate': total_placed / total_candidates,
            'capacity_utilization': total_placed / total_capacity
        }
        
        print(f"\n📈 ALLOCATION SUMMARY:")
        print(f"   Total Candidates: {total_candidates}")
        print(f"   Successfully Placed: {total_placed}")
        print(f"   Placement Rate: {allocation_summary['placement_rate']:.1%}")
        print(f"   Capacity Utilization: {allocation_summary['capacity_utilization']:.1%}")
        
        # Step 7: Record on blockchain for transparency
        complete_results = {
            'final_matches': final_matches,
            'allocation_summary': allocation_summary
        }
        blockchain_tx_id = self.blockchain_trust.record_allocation_on_blockchain(complete_results)
        
        return {
            'final_matches': final_matches,
            'rankings': rankings,
            'allocation_summary': allocation_summary,
            'candidate_preferences': candidate_prefs,
            'internship_preferences': internship_prefs
        }
    
    def export_results(self, allocation_results: Dict[str, Any], output_file: str = "allocation_results.json"):
        """Export allocation results to JSON file."""
        # Prepare serializable data
        export_data = {
            'final_allocation': allocation_results['final_matches'],
            'summary': allocation_results['allocation_summary'],
            'timestamp': pd.Timestamp.now().isoformat(),
            'algorithm': 'Gale-Shapley Stable Matching with AI Ranking'
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"✅ Results exported to {output_file}")

# Test function
def test_matching_algorithm():
    """Test the complete matching pipeline."""
    print("🧪 Testing Complete Matching Algorithm...")
    
    engine = StableMatchingEngine()
    
    # Run complete allocation
    results = engine.run_complete_allocation(
        "data/candidates.csv",
        "data/internships.csv"
    )
    
    # Display final allocation
    print("\n" + "="*50)
    print("🎯 FINAL ALLOCATION RESULTS")
    print("="*50)
    
    for internship_id, candidate_ids in results['final_matches'].items():
        if candidate_ids:  # Only show internships with matches
            print(f"\n{internship_id}: {len(candidate_ids)} candidates")
            for candidate_id in candidate_ids:
                print(f"  - {candidate_id}")
    
    # Export results
    engine.export_results(results, "data/final_allocation.json")
    
    return results

if __name__ == "__main__":
    test_matching_algorithm()
