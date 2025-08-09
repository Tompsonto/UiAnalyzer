"""
Scoring Engine - Combines visual and text analysis into final scores
"""
from typing import Dict, Any, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ScoringEngine:
    
    def __init__(self):
        # Overall scoring weights
        self.weights = {
            'visual': 0.6,  # Visual clarity is weighted higher for UX
            'text': 0.4
        }
    
    def calculate_overall_score(self, visual_result: Dict[str, Any], text_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine visual and text analysis into final clarity score
        """
        try:
            visual_score = visual_result.get('visual_score', 0)
            text_score = text_result.get('text_score', 0)
            
            # Calculate weighted overall score
            overall_score = (
                visual_score * self.weights['visual'] +
                text_score * self.weights['text']
            )
            
            # Combine issues from both analyses
            all_issues = []
            all_issues.extend(visual_result.get('issues', []))
            all_issues.extend(text_result.get('issues', []))
            
            # Sort issues by severity
            severity_order = {'high': 3, 'medium': 2, 'low': 1, 'info': 0}
            all_issues.sort(key=lambda x: severity_order.get(x.get('severity', 'info'), 0), reverse=True)
            
            # Combine recommendations
            all_recommendations = []
            all_recommendations.extend(visual_result.get('recommendations', []))
            all_recommendations.extend(text_result.get('recommendations', []))
            
            # Remove duplicate recommendations
            seen_actions = set()
            unique_recommendations = []
            for rec in all_recommendations:
                action = rec.get('action', '')
                if action and action not in seen_actions:
                    seen_actions.add(action)
                    unique_recommendations.append(rec)
            
            # Sort by priority
            priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
            unique_recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'Low'), 1), reverse=True)
            
            # Generate summary
            summary = self._generate_summary(overall_score, visual_score, text_score, all_issues)
            
            # Create final result
            result = {
                'overall_score': round(overall_score, 1),
                'visual_score': visual_score,
                'text_score': text_score,
                'score_breakdown': {
                    'visual': visual_result.get('score_breakdown', {}),
                    'text': text_result.get('score_breakdown', {})
                },
                'grade': self._get_score_grade(overall_score),
                'summary': summary,
                'total_issues': len(all_issues),
                'critical_issues': len([i for i in all_issues if i.get('severity') == 'high']),
                'issues': all_issues[:20],  # Limit to top 20 issues
                'recommendations': unique_recommendations[:10],  # Limit to top 10 recommendations
                'metrics': {
                    'visual_metrics': visual_result.get('score_breakdown', {}),
                    'text_metrics': text_result.get('metrics', {}),
                    'analysis_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Scoring error: {str(e)}")
            return {
                'overall_score': 0,
                'visual_score': 0,
                'text_score': 0,
                'grade': 'F',
                'summary': f'Analysis failed: {str(e)}',
                'total_issues': 1,
                'critical_issues': 1,
                'issues': [{'type': 'error', 'severity': 'high', 'message': str(e)}],
                'recommendations': [],
                'metrics': {}
            }
    
    def _get_score_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_summary(self, overall_score: float, visual_score: float, text_score: float, issues: List[Dict]) -> str:
        """Generate human-readable summary of analysis"""
        
        grade = self._get_score_grade(overall_score)
        critical_issues = len([i for i in issues if i.get('severity') == 'high'])
        
        # Base summary based on overall score
        if overall_score >= 90:
            base_summary = "Excellent clarity! Your website has outstanding visual design and text readability."
        elif overall_score >= 80:
            base_summary = "Good clarity with room for improvement. Most users will have a positive experience."
        elif overall_score >= 70:
            base_summary = "Moderate clarity. Some users may struggle with readability or visual elements."
        elif overall_score >= 60:
            base_summary = "Below average clarity. Significant improvements needed for better user experience."
        else:
            base_summary = "Poor clarity. Major issues detected that likely impact user engagement and conversions."
        
        # Add specific insights
        insights = []
        
        if visual_score < text_score - 10:
            insights.append("Visual design needs more attention than content.")
        elif text_score < visual_score - 10:
            insights.append("Content readability could be improved.")
        
        if critical_issues > 5:
            insights.append(f"{critical_issues} critical issues require immediate attention.")
        elif critical_issues > 0:
            insights.append(f"{critical_issues} high-priority issues detected.")
        
        # Combine summary
        full_summary = base_summary
        if insights:
            full_summary += " " + " ".join(insights)
        
        return full_summary
    
    def generate_comparison_data(self, current_score: float) -> Dict[str, Any]:
        """Generate comparison data for dashboard"""
        
        # Simulated benchmark data (in production, this would come from database)
        industry_average = 74.2
        top_quartile = 85.0
        
        comparison = {
            'vs_industry_average': round(current_score - industry_average, 1),
            'percentile': self._calculate_percentile(current_score),
            'industry_average': industry_average,
            'top_quartile': top_quartile,
            'improvement_potential': max(0, round(top_quartile - current_score, 1))
        }
        
        return comparison
    
    def _calculate_percentile(self, score: float) -> int:
        """Calculate approximate percentile based on score"""
        # Simplified percentile calculation
        if score >= 95:
            return 95
        elif score >= 85:
            return 80
        elif score >= 75:
            return 65
        elif score >= 65:
            return 50
        elif score >= 55:
            return 35
        elif score >= 45:
            return 20
        else:
            return 10
    
    def calculate_improvement_impact(self, issues: List[Dict]) -> Dict[str, Any]:
        """Calculate potential score improvement if issues are fixed"""
        
        potential_gains = {
            'high': 5,    # High severity issues worth 5 points each when fixed
            'medium': 3,  # Medium severity issues worth 3 points each
            'low': 1      # Low severity issues worth 1 point each
        }
        
        max_improvement = 0
        issue_breakdown = {'high': 0, 'medium': 0, 'low': 0}
        
        for issue in issues:
            severity = issue.get('severity', 'low')
            if severity in potential_gains:
                max_improvement += potential_gains[severity]
                issue_breakdown[severity] += 1
        
        return {
            'max_potential_improvement': min(max_improvement, 30),  # Cap at 30 points
            'issue_breakdown': issue_breakdown,
            'quick_wins': issue_breakdown['low'] + issue_breakdown['medium'],
            'high_impact_fixes': issue_breakdown['high']
        }