"""
Stable Matching Algorithm Implementation for PMIS-AI Engine
Implements Gale-Shapley algorithm with capacity and quota constraints
"""

import pandas as pd
from typing import Dict, List, Tuple, Set
from collections import defaultdict, deque
import random

class StableMatchingAlgorithm:
    def __init__(self):
        self.matches = {}
        self.internship_capacities = {}
        self.internship_current_matches = defaultdict(list)
        self.candidate_proposals = defaultdict(int)
        
    def load_data(self, candidates_file: str, internships_file: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Load candidate and internship data from CSV files
        
        Args:
            candidates_file: Path to candidates CSV
            internships_file: Path to internships CSV
            
        Returns:
            Tuple[List[Dict], List[Dict]]: (candidates, internships)
        """
        try:
            # Load candidates
            candidates_df = pd.read_csv(candidates_file)
            candidates = candidates_df.to_dict('records')
            
            # Load internships
            internships_df = pd.read_csv(internships_file)
            internships = internships_df.to_dict('records')
            
            # Store capacities
            for internship in internships:
                self.internship_capacities[internship['internship_id']] = internship['capacity']
            
            print(f"✅ Loaded {len(candidates)} candidates and {len(internships)} internships")
            return candidates, internships
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return [], []

    def check_quota_constraints(self, matches: Dict, candidates: List[Dict]) -> Dict:
        """
        Check and enforce affirmative action quotas
        
        Args:
            matches: Current matching results
            candidates: List of all candidates
            
        Returns:
            Dict: Quota compliance statistics
        """
        # Create candidate lookup
        candidate_lookup = {c['candidate_id']: c for c in candidates}
        
        # Count allocations by category
        total_allocated = len(matches)
        rural_count = 0
        category_counts = defaultdict(int)
        
        for candidate_id in matches.keys():
            candidate = candidate_lookup.get(candidate_id)
            if candidate:
                if candidate.get('is_rural', False):
                    rural_count += 1
                category_counts[candidate.get('social_category', 'General')] += 1
        
        # Calculate percentages
        rural_percentage = (rural_count / total_allocated * 100) if total_allocated > 0 else 0
        
        quota_stats = {
            'total_allocated': total_allocated,
            'rural_count': rural_count,
            'rural_percentage': round(rural_percentage, 2),
            'category_distribution': dict(category_counts),
            'meets_rural_quota': rural_percentage >= 30.0  # 30% rural quota
        }
        
        return quota_stats

    def apply_quota_boost(self, candidate_preferences: Dict, internship_preferences: Dict, 
                         candidates: List[Dict]) -> Tuple[Dict, Dict]:
        """
        Apply quota-based preference boosting for affirmative action
        
        Args:
            candidate_preferences: Original candidate preferences
            internship_preferences: Original internship preferences
            candidates: List of all candidates
            
        Returns:
            Tuple[Dict, Dict]: Modified preferences with quota boosting
        """
        candidate_lookup = {c['candidate_id']: c for c in candidates}
        
        # Boost preferences for rural and reserved category candidates
        boosted_internship_preferences = {}
        
        for internship_id, pref_list in internship_preferences.items():
            boosted_list = []
            regular_list = []
            
            for candidate_id in pref_list:
                candidate = candidate_lookup.get(candidate_id)
                if candidate:
                    # Boost rural candidates and reserved categories
                    if (candidate.get('is_rural', False) or 
                        candidate.get('social_category') in ['SC', 'ST', 'OBC']):
                        boosted_list.append(candidate_id)
                    else:
                        regular_list.append(candidate_id)
            
            # Interleave boosted and regular candidates (2:1 ratio for quota compliance)
            final_list = []
            i = j = 0
            while i < len(boosted_list) or j < len(regular_list):
                # Add 2 boosted candidates
                for _ in range(2):
                    if i < len(boosted_list):
                        final_list.append(boosted_list[i])
                        i += 1
                
                # Add 1 regular candidate
                if j < len(regular_list):
                    final_list.append(regular_list[j])
                    j += 1
            
            boosted_internship_preferences[internship_id] = final_list
        
        return candidate_preferences, boosted_internship_preferences

    def run_stable_matching(self, candidate_preferences: Dict, internship_preferences: Dict,
                           candidates: List[Dict], apply_quotas: bool = True) -> Dict:
        """
        Execute Gale-Shapley stable matching algorithm with capacity constraints
        
        Args:
            candidate_preferences: Candidate preference lists
            internship_preferences: Internship preference lists
            candidates: List of all candidates
            apply_quotas: Whether to apply affirmative action quotas
            
        Returns:
            Dict: Final matching results
        """
        print("🔄 Running Stable Matching Algorithm...")
        
        # Apply quota boosting if enabled
        if apply_quotas:
            candidate_preferences, internship_preferences = self.apply_quota_boost(
                candidate_preferences, internship_preferences, candidates
            )
        
        # Initialize data structures
        free_candidates = set(candidate_preferences.keys())
        self.matches = {}
        self.internship_current_matches = defaultdict(list)
        self.candidate_proposals = defaultdict(int)
        
        # Create internship preference rankings for O(1) lookup
        internship_rankings = {}
        for internship_id, pref_list in internship_preferences.items():
            internship_rankings[internship_id] = {
                candidate_id: rank for rank, candidate_id in enumerate(pref_list)
            }
        
        iteration = 0
        max_iterations = len(candidate_preferences) * len(internship_preferences)
        
        while free_candidates and iteration < max_iterations:
            iteration += 1
            
            # Pick a free candidate
            candidate_id = free_candidates.pop()
            
            # Get candidate's next preferred internship
            proposal_index = self.candidate_proposals[candidate_id]
            candidate_prefs = candidate_preferences.get(candidate_id, [])
            
            if proposal_index >= len(candidate_prefs):
                # Candidate has exhausted all preferences
                continue
            
            internship_id = candidate_prefs[proposal_index]
            self.candidate_proposals[candidate_id] += 1
            
            # Check if internship exists in preferences
            if internship_id not in internship_preferences:
                free_candidates.add(candidate_id)
                continue
            
            # Check if candidate is acceptable to internship
            if candidate_id not in internship_rankings.get(internship_id, {}):
                free_candidates.add(candidate_id)
                continue
            
            capacity = self.internship_capacities.get(internship_id, 1)
            current_matches = self.internship_current_matches[internship_id]
            
            if len(current_matches) < capacity:
                # Internship has space - accept candidate
                self.matches[candidate_id] = internship_id
                current_matches.append(candidate_id)
            else:
                # Internship is full - find worst current match
                worst_candidate = None
                worst_rank = -1
                
                for matched_candidate in current_matches:
                    rank = internship_rankings[internship_id].get(matched_candidate, float('inf'))
                    if rank > worst_rank:
                        worst_rank = rank
                        worst_candidate = matched_candidate
                
                # Check if new candidate is better than worst current match
                new_candidate_rank = internship_rankings[internship_id].get(candidate_id, float('inf'))
                
                if new_candidate_rank < worst_rank:
                    # Replace worst candidate with new candidate
                    if worst_candidate in self.matches:
                        del self.matches[worst_candidate]
                    current_matches.remove(worst_candidate)
                    free_candidates.add(worst_candidate)
                    
                    self.matches[candidate_id] = internship_id
                    current_matches.append(candidate_id)
                else:
                    # New candidate is worse - reject
                    free_candidates.add(candidate_id)
        
        print(f"✅ Stable matching completed in {iteration} iterations")
        print(f"📊 Total matches: {len(self.matches)}")
        
        # Check quota compliance
        quota_stats = self.check_quota_constraints(self.matches, candidates)
        print(f"🎯 Rural quota: {quota_stats['rural_percentage']}% (target: 30%)")
        print(f"📈 Quota compliance: {'✅ Met' if quota_stats['meets_rural_quota'] else '❌ Not met'}")
        
        return {
            'matches': self.matches,
            'quota_stats': quota_stats,
            'iterations': iteration,
            'algorithm_success': True
        }

    def verify_stability(self, matches: Dict, candidate_preferences: Dict, 
                        internship_preferences: Dict) -> bool:
        """
        Verify that the matching is stable (no blocking pairs exist)
        
        Args:
            matches: Final matching
            candidate_preferences: Candidate preferences
            internship_preferences: Internship preferences
            
        Returns:
            bool: True if matching is stable
        """
        # Create reverse lookup for internship matches
        internship_matches = defaultdict(list)
        for candidate_id, internship_id in matches.items():
            internship_matches[internship_id].append(candidate_id)
        
        # Check for blocking pairs
        for candidate_id, current_internship in matches.items():
            candidate_prefs = candidate_preferences.get(candidate_id, [])
            
            # Check all internships candidate prefers over current match
            current_rank = candidate_prefs.index(current_internship) if current_internship in candidate_prefs else len(candidate_prefs)
            
            for i in range(current_rank):
                preferred_internship = candidate_prefs[i]
                internship_prefs = internship_preferences.get(preferred_internship, [])
                
                if candidate_id not in internship_prefs:
                    continue
                
                candidate_rank_at_internship = internship_prefs.index(candidate_id)
                current_matches_at_internship = internship_matches[preferred_internship]
                
                # Check if internship would prefer this candidate over any current match
                for matched_candidate in current_matches_at_internship:
                    if matched_candidate in internship_prefs:
                        matched_rank = internship_prefs.index(matched_candidate)
                        if candidate_rank_at_internship < matched_rank:
                            print(f"❌ Blocking pair found: Candidate {candidate_id} and Internship {preferred_internship}")
                            return False
        
        print("✅ Matching is stable - no blocking pairs found")
        return True

    def export_results(self, results: Dict, candidates: List[Dict], 
                      internships: List[Dict], output_file: str = "allocation_results.csv"):
        """
        Export matching results to CSV file
        
        Args:
            results: Matching results
            candidates: List of candidates
            internships: List of internships
            output_file: Output CSV filename
        """
        try:
            # Create lookups
            candidate_lookup = {c['candidate_id']: c for c in candidates}
            internship_lookup = {i['internship_id']: i for i in internships}
            
            # Prepare export data
            export_data = []
            
            for candidate_id, internship_id in results['matches'].items():
                candidate = candidate_lookup.get(candidate_id, {})
                internship = internship_lookup.get(internship_id, {})
                
                export_data.append({
                    'candidate_id': candidate_id,
                    'candidate_name': candidate.get('name', 'Unknown'),
                    'age': candidate.get('age', 'N/A'),
                    'social_category': candidate.get('social_category', 'General'),
                    'is_rural': candidate.get('is_rural', False),
                    'internship_id': internship_id,
                    'company_name': internship.get('company_name', 'Unknown'),
                    'job_title': internship.get('job_title', 'Unknown'),
                    'location': internship.get('location', 'Unknown'),
                    'sector': internship.get('sector', 'Unknown')
                })
            
            # Create DataFrame and export
            df = pd.DataFrame(export_data)
            df.to_csv(output_file, index=False)
            
            print(f"✅ Results exported to {output_file}")
            print(f"📄 Total allocations: {len(export_data)}")
            
        except Exception as e:
            print(f"❌ Error exporting results: {str(e)}")


# Test function
if __name__ == "__main__":
    print("=== Testing Stable Matching Algorithm ===")
    
    matcher = StableMatchingAlgorithm()
    
    # Load test data
    candidates, internships = matcher.load_data(
        "data/candidates.csv", 
        "data/internships.csv"
    )
    
    if candidates and internships:
        # For testing, create simple preference lists
        from ranking_engine import RankingEngine
        
        engine = RankingEngine()
        candidate_prefs, internship_prefs = engine.generate_preference_lists(candidates, internships)
        
        # Run matching
        results = matcher.run_stable_matching(candidate_prefs, internship_prefs, candidates)
        
        # Verify stability
        matcher.verify_stability(results['matches'], candidate_prefs, internship_prefs)
        
        # Export results
        matcher.export_results(results, candidates, internships)
        
        print("\n=== Matching Summary ===")
        print(f"Total matches: {len(results['matches'])}")
        print(f"Quota statistics: {results['quota_stats']}")
    else:
        print("❌ Failed to load test data")
