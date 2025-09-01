import pandas as pd
from typing import List, Dict, Any, Tuple
from ranking_engine import RankingEngine
from resume_parser import ResumeParser

class MatchingAlgorithm:
    def __init__(self):
        """
        Initialize the matching algorithm with ranking engine and resume parser
        """
        self.ranking_engine = RankingEngine()
        self.resume_parser = ResumeParser()
    
    def load_data(self, candidates_csv: str, internships_csv: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load candidate and internship data from CSV files
        """
        try:
            candidates_df = pd.read_csv(candidates_csv)
            internships_df = pd.read_csv(internships_csv)
            return candidates_df, internships_df
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def calculate_all_scores(self, candidates_df: pd.DataFrame, internships_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Calculate matching scores for all candidate-job pairs
        """
        scores = []
        
        for _, candidate in candidates_df.iterrows():
            for _, job in internships_df.iterrows():
                # Create candidate data structure
                candidate_data = {
                    'id': candidate['id'],
                    'name': candidate['name'],
                    'email': candidate['email'],
                    'skills': candidate['skills'].split(', '),
                    'experience_years': candidate['experience_years'],
                    'gpa': candidate['gpa'],
                    'university': candidate['university'],
                    'text': f"{candidate['name']} - {candidate['skills']} - {candidate['university']}"
                }
                
                # Create job data structure
                job_data = {
                    'id': job['id'],
                    'title': job['title'],
                    'company': job['company'],
                    'description': job['description'],
                    'required_skills': job['required_skills'].split(', '),
                    'spots_available': job['spots_available'],
                    'salary': job['salary']
                }
                
                # Calculate comprehensive score
                score = self.ranking_engine.calculate_comprehensive_score(candidate_data, job_data)
                
                scores.append({
                    'candidate_id': candidate['id'],
                    'candidate_name': candidate['name'],
                    'job_id': job['id'],
                    'job_title': job['title'],
                    'company': job['company'],
                    'score': score
                })
        
        return scores
    
    def greedy_matching(self, scores: List[Dict[str, Any]], candidates_df: pd.DataFrame, internships_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Implement greedy matching algorithm
        For each internship spot, find the available candidate with the highest score
        """
        # Sort scores by score in descending order
        sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
        
        # Track available spots for each job
        available_spots = {}
        for _, job in internships_df.iterrows():
            available_spots[job['id']] = job['spots_available']
        
        # Track assigned candidates
        assigned_candidates = set()
        
        # Track final allocations
        allocations = []
        
        for score_entry in sorted_scores:
            candidate_id = score_entry['candidate_id']
            job_id = score_entry['job_id']
            
            # Skip if candidate is already assigned or job has no spots left
            if candidate_id in assigned_candidates or available_spots[job_id] <= 0:
                continue
            
            # Make the assignment
            allocation = {
                'candidate_id': candidate_id,
                'candidate_name': score_entry['candidate_name'],
                'job_id': job_id,
                'job_title': score_entry['job_title'],
                'company': score_entry['company'],
                'score': score_entry['score'],
                'allocation_id': len(allocations) + 1
            }
            
            allocations.append(allocation)
            assigned_candidates.add(candidate_id)
            available_spots[job_id] -= 1
        
        return allocations
    
    def run_complete_matching(self, candidates_csv: str, internships_csv: str) -> Dict[str, Any]:
        """
        Run the complete matching process
        """
        try:
            # Load data
            candidates_df, internships_df = self.load_data(candidates_csv, internships_csv)
            
            # Calculate all scores
            scores = self.calculate_all_scores(candidates_df, internships_df)
            
            # Run greedy matching
            allocations = self.greedy_matching(scores, candidates_df, internships_df)
            
            # Prepare results
            results = {
                'allocations': allocations,
                'total_allocations': len(allocations),
                'total_candidates': len(candidates_df),
                'total_jobs': len(internships_df),
                'matching_efficiency': len(allocations) / len(candidates_df) if len(candidates_df) > 0 else 0,
                'scores_summary': {
                    'max_score': max(scores, key=lambda x: x['score'])['score'] if scores else 0,
                    'min_score': min(scores, key=lambda x: x['score'])['score'] if scores else 0,
                    'avg_score': sum(s['score'] for s in scores) / len(scores) if scores else 0
                }
            }
            
            return results
            
        except Exception as e:
            raise Exception(f"Error in matching process: {str(e)}")
    
    def get_unassigned_candidates(self, allocations: List[Dict[str, Any]], candidates_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get list of candidates who were not assigned to any job
        """
        assigned_candidate_ids = {alloc['candidate_id'] for alloc in allocations}
        unassigned = []
        
        for _, candidate in candidates_df.iterrows():
            if candidate['id'] not in assigned_candidate_ids:
                unassigned.append({
                    'id': candidate['id'],
                    'name': candidate['name'],
                    'email': candidate['email'],
                    'skills': candidate['skills'],
                    'experience_years': candidate['experience_years'],
                    'gpa': candidate['gpa'],
                    'university': candidate['university']
                })
        
        return unassigned
    
    def get_unfilled_jobs(self, allocations: List[Dict[str, Any]], internships_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Get list of jobs that still have unfilled spots
        """
        # Count allocations per job
        job_allocation_counts = {}
        for alloc in allocations:
            job_id = alloc['job_id']
            job_allocation_counts[job_id] = job_allocation_counts.get(job_id, 0) + 1
        
        unfilled = []
        for _, job in internships_df.iterrows():
            allocated_count = job_allocation_counts.get(job['id'], 0)
            remaining_spots = job['spots_available'] - allocated_count
            
            if remaining_spots > 0:
                unfilled.append({
                    'id': job['id'],
                    'title': job['title'],
                    'company': job['company'],
                    'description': job['description'],
                    'required_skills': job['required_skills'],
                    'spots_available': job['spots_available'],
                    'filled_spots': allocated_count,
                    'remaining_spots': remaining_spots,
                    'salary': job['salary']
                })
        
        return unfilled

# Example usage
if __name__ == "__main__":
    # Initialize matching algorithm
    matcher = MatchingAlgorithm()
    
    # Run complete matching
    try:
        results = matcher.run_complete_matching("data/candidates.csv", "data/internships.csv")
        
        print("Matching Results:")
        print(f"Total allocations: {results['total_allocations']}")
        print(f"Matching efficiency: {results['matching_efficiency']:.2%}")
        print(f"Score range: {results['scores_summary']['min_score']:.4f} - {results['scores_summary']['max_score']:.4f}")
        
        print("\nAllocations:")
        for alloc in results['allocations']:
            print(f"{alloc['candidate_name']} -> {alloc['job_title']} at {alloc['company']} (Score: {alloc['score']:.4f})")
            
    except Exception as e:
        print(f"Error: {e}")
