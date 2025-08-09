"""
Text Readability Analysis Module - Analyzes language complexity and structure
"""
import re
from typing import Dict, List, Any
import logging
import textstat
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class TextAnalyzer:
    
    def __init__(self):
        self.issues = []
        self.score_components = {}
    
    def analyze_text_readability(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main text analysis function
        Returns text readability score and issues
        """
        self.issues = []
        self.score_components = {}
        
        try:
            text_content = page_data.get('text_content', '')
            html_content = page_data.get('html_content', '')
            
            if not text_content:
                return {
                    'text_score': 0,
                    'score_breakdown': {},
                    'issues': [{'type': 'error', 'message': 'No text content found'}],
                    'recommendations': []
                }
            
            # Analyze different text aspects
            readability_score = self._analyze_readability(text_content)
            structure_score = self._analyze_structure(html_content, page_data)
            complexity_score = self._analyze_complexity(text_content)
            
            # Calculate weighted overall score
            weights = {
                'readability': 0.4,
                'structure': 0.3,
                'complexity': 0.3
            }
            
            text_score = (
                readability_score * weights['readability'] +
                structure_score * weights['structure'] +
                complexity_score * weights['complexity']
            )
            
            return {
                'text_score': round(text_score, 1),
                'score_breakdown': {
                    'readability': readability_score,
                    'structure': structure_score,
                    'complexity': complexity_score
                },
                'issues': self.issues,
                'recommendations': self._generate_recommendations(),
                'metrics': self._get_text_metrics(text_content)
            }
            
        except Exception as e:
            logger.error(f"Text analysis error: {str(e)}")
            return {
                'text_score': 0,
                'score_breakdown': {},
                'issues': [{'type': 'error', 'message': f'Analysis failed: {str(e)}'}],
                'recommendations': []
            }
    
    def _analyze_readability(self, text: str) -> float:
        """Analyze text readability using various metrics"""
        score = 100
        
        try:
            # Flesch Reading Ease (0-100, higher is better)
            flesch_score = textstat.flesch_reading_ease(text)
            
            # Flesch-Kincaid Grade Level
            fk_grade = textstat.flesch_kincaid().grade
            
            # Gunning Fog Index
            fog_index = textstat.gunning_fog(text)
            
            # SMOG Index
            smog_index = textstat.smog_index(text)
            
            # Penalize poor readability scores
            if flesch_score < 30:  # Very difficult
                score -= 30
                self.issues.append({
                    'type': 'readability',
                    'severity': 'high',
                    'metric': 'Flesch Reading Ease',
                    'value': flesch_score,
                    'message': 'Text is very difficult to read',
                    'suggestion': 'Simplify language and use shorter sentences'
                })
            elif flesch_score < 50:  # Difficult
                score -= 15
                self.issues.append({
                    'type': 'readability',
                    'severity': 'medium',
                    'metric': 'Flesch Reading Ease',
                    'value': flesch_score,
                    'message': 'Text is somewhat difficult to read',
                    'suggestion': 'Consider simplifying complex sentences'
                })
            
            # Penalize high grade levels
            if fk_grade > 12:
                score -= 20
                self.issues.append({
                    'type': 'readability',
                    'severity': 'high',
                    'metric': 'Grade Level',
                    'value': fk_grade,
                    'message': f'Text requires {fk_grade:.1f} grade reading level',
                    'suggestion': 'Target 8th-10th grade reading level for broader audience'
                })
            
            # Penalize high fog index
            if fog_index > 12:
                score -= 15
                self.issues.append({
                    'type': 'readability',
                    'severity': 'medium',
                    'metric': 'Gunning Fog',
                    'value': fog_index,
                    'message': 'Complex sentence structure detected',
                    'suggestion': 'Break up long sentences and reduce complex words'
                })
            
        except Exception as e:
            logger.warning(f"Readability analysis error: {e}")
            score = 50  # Default middle score if analysis fails
        
        return max(0, score)
    
    def _analyze_structure(self, html_content: str, page_data: Dict[str, Any]) -> float:
        """Analyze text structure and hierarchy"""
        score = 100
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Analyze heading structure
        headings = page_data.get('dom_analysis', {}).get('headings', [])
        
        # Check for proper H1 usage
        h1_count = len([h for h in headings if h.get('tag') == 'H1'])
        if h1_count == 0:
            score -= 25
            self.issues.append({
                'type': 'structure',
                'severity': 'high',
                'element': 'H1',
                'message': 'No H1 heading found',
                'suggestion': 'Add a clear H1 heading that describes the page purpose'
            })
        elif h1_count > 1:
            score -= 15
            self.issues.append({
                'type': 'structure',
                'severity': 'medium',
                'element': 'H1',
                'message': f'Multiple H1 headings found: {h1_count}',
                'suggestion': 'Use only one H1 per page for better SEO and structure'
            })
        
        # Check heading hierarchy
        if not self._has_logical_heading_hierarchy(headings):
            score -= 10
            self.issues.append({
                'type': 'structure',
                'severity': 'low',
                'element': 'Headings',
                'message': 'Heading hierarchy is not logical',
                'suggestion': 'Use headings in order (H1 → H2 → H3) without skipping levels'
            })
        
        # Check for wall of text (paragraphs too long)
        paragraphs = soup.find_all('p')
        long_paragraphs = 0
        
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 300:  # More than 300 characters
                long_paragraphs += 1
        
        if long_paragraphs > 2:
            score -= 15
            self.issues.append({
                'type': 'structure',
                'severity': 'medium',
                'element': 'Paragraphs',
                'message': f'{long_paragraphs} very long paragraphs detected',
                'suggestion': 'Break up long paragraphs into shorter, scannable chunks'
            })
        
        return max(0, score)
    
    def _empty_result(self, message: str) -> Dict[str, Any]:
        """Return empty result with error message"""
        return {
            'text_score': 0,
            'score_breakdown': {},
            'issues': [{'type': 'error', 'severity': 'high', 'message': message}],
            'recommendations': [],
            'text_metrics': {}
        }
    
    def _analyze_complexity(self, text: str) -> float:
        """Analyze language complexity"""
        score = 100
        
        # Check average sentence length
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        if sentence_lengths:
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
            
            if avg_sentence_length > 25:
                score -= 20
                self.issues.append({
                    'type': 'complexity',
                    'severity': 'high',
                    'metric': 'Sentence Length',
                    'value': avg_sentence_length,
                    'message': f'Average sentence length is {avg_sentence_length:.1f} words',
                    'suggestion': 'Keep sentences under 20 words for better readability'
                })
            elif avg_sentence_length > 20:
                score -= 10
                self.issues.append({
                    'type': 'complexity',
                    'severity': 'low',
                    'metric': 'Sentence Length',
                    'value': avg_sentence_length,
                    'message': f'Sentences are somewhat long ({avg_sentence_length:.1f} words average)',
                    'suggestion': 'Consider shortening some sentences'
                })
        
        # Check for passive voice (basic detection)
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are', 'am']
        passive_count = 0
        total_sentences = len(sentence_lengths)
        
        for sentence in sentences[:50]:  # Check first 50 sentences
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in passive_indicators):
                if re.search(r'\\b(was|were|been|being)\\s+\\w+ed\\b', sentence_lower):
                    passive_count += 1
        
        if total_sentences > 0:
            passive_percentage = (passive_count / min(total_sentences, 50)) * 100
            
            if passive_percentage > 20:
                score -= 15
                self.issues.append({
                    'type': 'complexity',
                    'severity': 'medium',
                    'metric': 'Passive Voice',
                    'value': passive_percentage,
                    'message': f'{passive_percentage:.1f}% of sentences use passive voice',
                    'suggestion': 'Use active voice to make content more engaging and clear'
                })
        
        # Check for jargon and complex words
        words = re.findall(r'\\b\\w+\\b', text.lower())
        long_words = [w for w in words if len(w) > 8]
        long_word_percentage = (len(long_words) / len(words)) * 100 if words else 0
        
        if long_word_percentage > 15:
            score -= 10
            self.issues.append({
                'type': 'complexity',
                'severity': 'low',
                'metric': 'Complex Words',
                'value': long_word_percentage,
                'message': f'{long_word_percentage:.1f}% of words are complex (8+ characters)',
                'suggestion': 'Replace complex words with simpler alternatives where possible'
            })
        
        return max(0, score)
    
    def _has_logical_heading_hierarchy(self, headings: List[Dict]) -> bool:
        """Check if headings follow logical hierarchy"""
        if not headings:
            return False
        
        heading_levels = []
        for heading in headings:
            tag = heading.get('tag', '')
            if tag in ['H1', 'H2', 'H3', 'H4', 'H5', 'H6']:
                level = int(tag[1])
                heading_levels.append(level)
        
        if not heading_levels:
            return False
        
        # Check if we start with H1
        if heading_levels[0] != 1:
            return False
        
        # Check for level jumping (e.g., H1 → H3)
        for i in range(1, len(heading_levels)):
            if heading_levels[i] > heading_levels[i-1] + 1:
                return False
        
        return True
    
    def _get_text_metrics(self, text: str) -> Dict[str, Any]:
        """Get detailed text metrics"""
        try:
            return {
                'word_count': len(text.split()),
                'character_count': len(text),
                'sentence_count': len(re.split(r'[.!?]+', text)),
                'paragraph_count': len(text.split('\\n\\n')),
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid().grade,
                'gunning_fog': textstat.gunning_fog(text),
                'smog_index': textstat.smog_index(text)
            }
        except:
            return {}
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on issues"""
        recommendations = []
        
        issue_types = [issue['type'] for issue in self.issues]
        
        if 'readability' in issue_types:
            recommendations.append({
                'category': 'Readability',
                'priority': 'High',
                'action': 'Simplify Language',
                'description': 'Use shorter sentences and simpler words to improve readability'
            })
        
        if 'structure' in issue_types:
            recommendations.append({
                'category': 'Content Structure',
                'priority': 'Medium',
                'action': 'Improve Text Organization',
                'description': 'Use proper headings hierarchy and break up long paragraphs'
            })
        
        if 'complexity' in issue_types:
            recommendations.append({
                'category': 'Writing Style',
                'priority': 'Medium',
                'action': 'Reduce Complexity',
                'description': 'Use active voice and replace complex words with simpler alternatives'
            })
        
        return recommendations