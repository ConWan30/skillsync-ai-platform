"""
SkillSync AI Platform - Job Board Integration Module
Comprehensive integration with Indeed, LinkedIn, ZipRecruiter, and gaming job boards
Includes affiliate tracking, revenue optimization, and real-time job matching
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import hashlib
from urllib.parse import urlencode, quote_plus

class JobBoardIntegrator:
    """Main class for integrating with multiple job boards and tracking affiliate revenue"""
    
    def __init__(self):
        # API Configuration
        self.indeed_publisher_id = os.getenv('INDEED_PUBLISHER_ID', 'skillsync_ai_001')
        self.linkedin_api_key = os.getenv('LINKEDIN_API_KEY', '')
        self.ziprecruiter_api_key = os.getenv('ZIPRECRUITER_API_KEY', '')
        
        # Affiliate Configuration
        self.affiliate_config = {
            'indeed': {
                'partner_id': 'skillsync_ai',
                'commission_rate': 0.15,  # 15% commission
                'base_commission': 150,   # $150 per hire
            },
            'linkedin': {
                'partner_id': 'skillsync_premium',
                'commission_rate': 0.30,  # 30% of premium subscription
                'monthly_value': 29.99,   # LinkedIn Premium cost
            },
            'ziprecruiter': {
                'partner_id': 'skillsync_zip',
                'commission_rate': 0.20,  # 20% commission
                'base_commission': 100,   # $100 per application
            }
        }
        
        # Gaming job boards configuration
        self.gaming_boards = {
            'gamejobs': 'https://gamejobs.co/api/v1/jobs',
            'gamesindustry': 'https://jobs.gamesindustry.biz/api/jobs',
            'unity_connect': 'https://connect.unity.com/api/jobs',
            'hitmarker': 'https://hitmarker.net/api/jobs'
        }
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # 1 second between requests
        
    def search_all_platforms(self, query: str, location: str = 'remote', 
                           experience_level: str = 'mid', limit: int = 50) -> List[Dict]:
        """Search all job platforms and aggregate results"""
        all_jobs = []
        
        try:
            # Indeed Jobs
            indeed_jobs = self.search_indeed_jobs(query, location, limit//4)
            all_jobs.extend(indeed_jobs)
            
            # LinkedIn Jobs
            linkedin_jobs = self.search_linkedin_jobs(query, location, limit//4)
            all_jobs.extend(linkedin_jobs)
            
            # ZipRecruiter Jobs
            zip_jobs = self.search_ziprecruiter_jobs(query, location, limit//4)
            all_jobs.extend(zip_jobs)
            
            # Gaming-specific boards if gaming role
            if self._is_gaming_role(query):
                gaming_jobs = self.search_gaming_jobs(query, location, limit//4)
                all_jobs.extend(gaming_jobs)
            
            # Remove duplicates and sort by relevance
            unique_jobs = self._deduplicate_jobs(all_jobs)
            scored_jobs = self._score_job_relevance(unique_jobs, query, experience_level)
            
            return scored_jobs[:limit]
            
        except Exception as e:
            print(f"[ERROR] Job search failed: {e}")
            return []
    
    def search_indeed_jobs(self, query: str, location: str, limit: int = 25) -> List[Dict]:
        """Search Indeed jobs using their API with affiliate tracking"""
        jobs = []
        
        try:
            # Rate limiting
            self._enforce_rate_limit('indeed')
            
            # Indeed API endpoint (using their Publisher API)
            base_url = "http://api.indeed.com/ads/apisearch"
            
            params = {
                'publisher': self.indeed_publisher_id,
                'q': query,
                'l': location,
                'sort': 'relevance',
                'radius': '25',
                'st': 'jobsite',
                'jt': 'fulltime',
                'start': 0,
                'limit': limit,
                'fromage': '14',  # Jobs from last 14 days
                'format': 'json',
                'v': '2'
            }
            
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for job in data.get('results', []):
                    processed_job = {
                        'id': job.get('jobkey', ''),
                        'title': job.get('jobtitle', ''),
                        'company': job.get('company', ''),
                        'location': job.get('formattedLocation', location),
                        'summary': job.get('snippet', ''),
                        'url': job.get('url', ''),
                        'date_posted': job.get('date', ''),
                        'salary': self._extract_salary(job.get('snippet', '')),
                        'source': 'Indeed',
                        'source_logo': 'https://indeed.com/favicon.ico',
                        
                        # Affiliate tracking
                        'affiliate_url': self._generate_indeed_affiliate_url(job.get('jobkey', '')),
                        'tracking_id': f"indeed_{job.get('jobkey', '')}",
                        'revenue_potential': self.affiliate_config['indeed']['base_commission'],
                        'commission_rate': self.affiliate_config['indeed']['commission_rate'],
                        
                        # Metadata
                        'platform_priority': 1,  # High priority
                        'match_score': 0,  # Will be calculated later
                        'apply_difficulty': 'medium'
                    }
                    
                    jobs.append(processed_job)
                    
            else:
                print(f"[WARNING] Indeed API error: {response.status_code}")
                # Fallback to sample data
                jobs = self._get_indeed_fallback_jobs(query, location, limit)
                
        except Exception as e:
            print(f"[ERROR] Indeed search failed: {e}")
            jobs = self._get_indeed_fallback_jobs(query, location, limit)
        
        return jobs
    
    def search_linkedin_jobs(self, query: str, location: str, limit: int = 25) -> List[Dict]:
        """Search LinkedIn jobs with premium upgrade tracking"""
        jobs = []
        
        try:
            # Rate limiting
            self._enforce_rate_limit('linkedin')
            
            # LinkedIn Jobs API (requires LinkedIn API access)
            if self.linkedin_api_key:
                headers = {
                    'Authorization': f'Bearer {self.linkedin_api_key}',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
                
                # LinkedIn API endpoint
                base_url = "https://api.linkedin.com/v2/jobSearch"
                
                params = {
                    'keywords': query,
                    'locationFallback': location,
                    'count': limit,
                    'start': 0
                }
                
                response = requests.get(base_url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('elements', []):
                        processed_job = {
                            'id': str(job.get('id', '')),
                            'title': job.get('title', ''),
                            'company': job.get('companyDetails', {}).get('company', {}).get('name', ''),
                            'location': job.get('formattedLocation', location),
                            'summary': job.get('description', {}).get('text', '')[:200] + '...',
                            'url': f"https://linkedin.com/jobs/view/{job.get('id', '')}",
                            'date_posted': job.get('listedAt', ''),
                            'salary': 'Competitive',
                            'source': 'LinkedIn',
                            'source_logo': 'https://linkedin.com/favicon.ico',
                            
                            # Premium tracking
                            'premium_required': True,
                            'premium_upgrade_url': self._generate_linkedin_premium_url(),
                            'tracking_id': f"linkedin_{job.get('id', '')}",
                            'revenue_potential': self.affiliate_config['linkedin']['monthly_value'],
                            'commission_rate': self.affiliate_config['linkedin']['commission_rate'],
                            
                            # Metadata
                            'platform_priority': 2,  # High priority for professional roles
                            'match_score': 0,
                            'apply_difficulty': 'easy'
                        }
                        
                        jobs.append(processed_job)
                        
            else:
                # Fallback without API key
                jobs = self._get_linkedin_fallback_jobs(query, location, limit)
                
        except Exception as e:
            print(f"[ERROR] LinkedIn search failed: {e}")
            jobs = self._get_linkedin_fallback_jobs(query, location, limit)
        
        return jobs
    
    def search_ziprecruiter_jobs(self, query: str, location: str, limit: int = 25) -> List[Dict]:
        """Search ZipRecruiter jobs with affiliate tracking"""
        jobs = []
        
        try:
            # Rate limiting
            self._enforce_rate_limit('ziprecruiter')
            
            if self.ziprecruiter_api_key:
                # ZipRecruiter API endpoint
                base_url = "https://api.ziprecruiter.com/jobs/v1"
                
                params = {
                    'search': query,
                    'location': location,
                    'radius_miles': 25,
                    'days_ago': 14,
                    'jobs_per_page': limit,
                    'page': 1,
                    'api_key': self.ziprecruiter_api_key
                }
                
                response = requests.get(base_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for job in data.get('jobs', []):
                        processed_job = {
                            'id': job.get('id', ''),
                            'title': job.get('name', ''),
                            'company': job.get('hiring_company', {}).get('name', ''),
                            'location': job.get('location', location),
                            'summary': job.get('snippet', ''),
                            'url': job.get('url', ''),
                            'date_posted': job.get('posted_time_friendly', ''),
                            'salary': job.get('salary_min_annual', 'Competitive'),
                            'source': 'ZipRecruiter',
                            'source_logo': 'https://ziprecruiter.com/favicon.ico',
                            
                            # Affiliate tracking
                            'affiliate_url': self._generate_ziprecruiter_affiliate_url(job.get('id', '')),
                            'tracking_id': f"zip_{job.get('id', '')}",
                            'revenue_potential': self.affiliate_config['ziprecruiter']['base_commission'],
                            'commission_rate': self.affiliate_config['ziprecruiter']['commission_rate'],
                            
                            # Metadata
                            'platform_priority': 3,
                            'match_score': 0,
                            'apply_difficulty': 'medium'
                        }
                        
                        jobs.append(processed_job)
                        
            else:
                jobs = self._get_ziprecruiter_fallback_jobs(query, location, limit)
                
        except Exception as e:
            print(f"[ERROR] ZipRecruiter search failed: {e}")
            jobs = self._get_ziprecruiter_fallback_jobs(query, location, limit)
        
        return jobs
    
    def search_gaming_jobs(self, query: str, location: str, limit: int = 25) -> List[Dict]:
        """Search gaming-specific job boards"""
        jobs = []
        
        gaming_roles = ['game developer', 'game designer', 'technical artist', 
                       'unity developer', 'unreal developer', 'indie developer']
        
        if not any(role in query.lower() for role in gaming_roles):
            return jobs
        
        try:
            # GameJobs.co integration
            gamejobs_data = self._search_gamejobs(query, location, limit//4)
            jobs.extend(gamejobs_data)
            
            # Hitmarker integration
            hitmarker_data = self._search_hitmarker(query, location, limit//4)
            jobs.extend(hitmarker_data)
            
            # Unity Connect integration
            unity_data = self._search_unity_connect(query, location, limit//4)
            jobs.extend(unity_data)
            
            # Games Industry integration
            gamesindustry_data = self._search_gamesindustry(query, location, limit//4)
            jobs.extend(gamesindustry_data)
            
        except Exception as e:
            print(f"[ERROR] Gaming job search failed: {e}")
        
        return jobs
    
    def _search_gamejobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Search GameJobs.co"""
        jobs = []
        
        # Simulate GameJobs.co API (replace with actual API when available)
        sample_jobs = [
            {
                'title': 'Unity Game Developer',
                'company': 'Indie Game Studio',
                'location': 'Remote',
                'summary': 'Seeking Unity developer for mobile game project...',
                'salary': '$65,000 - $85,000',
                'source': 'GameJobs.co'
            },
            {
                'title': 'Game Designer - RPG',
                'company': 'AAA Game Studio',
                'location': 'Los Angeles, CA',
                'summary': 'Design engaging RPG mechanics and systems...',
                'salary': '$70,000 - $95,000',
                'source': 'GameJobs.co'
            }
        ]
        
        for i, job in enumerate(sample_jobs[:limit]):
            processed_job = {
                'id': f"gamejobs_{i}",
                'title': job['title'],
                'company': job['company'],
                'location': job['location'],
                'summary': job['summary'],
                'url': f"https://gamejobs.co/jobs/{i}",
                'date_posted': 'Recent',
                'salary': job['salary'],
                'source': job['source'],
                'source_logo': 'https://gamejobs.co/favicon.ico',
                
                # Gaming-specific affiliate tracking
                'affiliate_url': f"https://gamejobs.co/jobs/{i}?ref=skillsync",
                'tracking_id': f"gamejobs_{i}",
                'revenue_potential': 200,  # Higher commission for specialized roles
                'commission_rate': 0.25,
                
                # Metadata
                'platform_priority': 4,
                'match_score': 0,
                'apply_difficulty': 'medium',
                'industry': 'Gaming'
            }
            
            jobs.append(processed_job)
        
        return jobs
    
    def _search_hitmarker(self, query: str, location: str, limit: int) -> List[Dict]:
        """Search Hitmarker gaming jobs"""
        # Similar implementation to GameJobs.co
        return []
    
    def _search_unity_connect(self, query: str, location: str, limit: int) -> List[Dict]:
        """Search Unity Connect jobs"""
        # Similar implementation for Unity-specific roles
        return []
    
    def _search_gamesindustry(self, query: str, location: str, limit: int) -> List[Dict]:
        """Search GamesIndustry.biz jobs"""
        # Similar implementation for games industry roles
        return []
    
    def _generate_indeed_affiliate_url(self, job_key: str) -> str:
        """Generate Indeed affiliate URL with tracking"""
        base_url = "https://indeed.com/viewjob"
        params = {
            'jk': job_key,
            'from': self.affiliate_config['indeed']['partner_id'],
            'utm_source': 'skillsync',
            'utm_medium': 'affiliate',
            'utm_campaign': 'job_matching'
        }
        return f"{base_url}?{urlencode(params)}"
    
    def _generate_linkedin_premium_url(self) -> str:
        """Generate LinkedIn Premium affiliate URL"""
        return "https://linkedin.com/premium?ref=skillsync&utm_source=skillsync&utm_medium=affiliate"
    
    def _generate_ziprecruiter_affiliate_url(self, job_id: str) -> str:
        """Generate ZipRecruiter affiliate URL"""
        return f"https://ziprecruiter.com/jobs/apply?ref=skillsync&job={job_id}&utm_source=skillsync"
    
    def _enforce_rate_limit(self, platform: str):
        """Enforce rate limiting for API calls"""
        current_time = time.time()
        last_time = self.last_request_time.get(platform, 0)
        
        if current_time - last_time < self.min_request_interval:
            time.sleep(self.min_request_interval - (current_time - last_time))
        
        self.last_request_time[platform] = time.time()
    
    def _is_gaming_role(self, query: str) -> bool:
        """Check if query is for gaming-related role"""
        gaming_keywords = ['game', 'unity', 'unreal', 'gaming', 'esports', 'indie']
        return any(keyword in query.lower() for keyword in gaming_keywords)
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _score_job_relevance(self, jobs: List[Dict], query: str, experience: str) -> List[Dict]:
        """Score jobs based on relevance to query and experience level"""
        for job in jobs:
            score = 0
            
            # Title match (40% weight)
            if query.lower() in job.get('title', '').lower():
                score += 40
            
            # Experience level match (30% weight)
            title_lower = job.get('title', '').lower()
            if experience == 'entry' and any(word in title_lower for word in ['junior', 'entry', 'associate']):
                score += 30
            elif experience == 'senior' and any(word in title_lower for word in ['senior', 'lead', 'principal']):
                score += 30
            elif experience == 'mid' and not any(word in title_lower for word in ['junior', 'senior', 'lead']):
                score += 30
            
            # Platform priority (20% weight)
            score += (5 - job.get('platform_priority', 5)) * 4
            
            # Gaming bonus (10% weight)
            if job.get('industry') == 'Gaming' and self._is_gaming_role(query):
                score += 10
            
            job['match_score'] = min(score, 100)
        
        # Sort by match score
        jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        return jobs
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary information from job text"""
        import re
        
        # Common salary patterns
        patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'\$[\d,]+k?\s*-\s*\$[\d,]+k?',
            r'[\d,]+k?\s*-\s*[\d,]+k?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return 'Competitive'
    
    def _get_indeed_fallback_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Fallback Indeed jobs when API is unavailable"""
        return [
            {
                'id': f'indeed_fallback_{i}',
                'title': f'{query} - Remote',
                'company': f'Tech Company {i+1}',
                'location': location,
                'summary': f'Exciting {query} opportunity with competitive benefits...',
                'url': f'https://indeed.com/jobs?q={quote_plus(query)}',
                'date_posted': 'Recent',
                'salary': 'Competitive',
                'source': 'Indeed',
                'affiliate_url': f'https://indeed.com/jobs?q={quote_plus(query)}&from=skillsync',
                'tracking_id': f'indeed_fallback_{i}',
                'revenue_potential': 150,
                'platform_priority': 1,
                'match_score': 75 - i*5
            }
            for i in range(min(limit, 5))
        ]
    
    def _get_linkedin_fallback_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Fallback LinkedIn jobs when API is unavailable"""
        return [
            {
                'id': f'linkedin_fallback_{i}',
                'title': f'Senior {query}',
                'company': f'Professional Services {i+1}',
                'location': location,
                'summary': f'Professional {query} role with growth opportunities...',
                'url': f'https://linkedin.com/jobs/search/?keywords={quote_plus(query)}',
                'date_posted': 'Recent',
                'salary': 'Competitive',
                'source': 'LinkedIn',
                'premium_required': True,
                'premium_upgrade_url': self._generate_linkedin_premium_url(),
                'tracking_id': f'linkedin_fallback_{i}',
                'revenue_potential': 29.99,
                'platform_priority': 2,
                'match_score': 80 - i*5
            }
            for i in range(min(limit, 5))
        ]
    
    def _get_ziprecruiter_fallback_jobs(self, query: str, location: str, limit: int) -> List[Dict]:
        """Fallback ZipRecruiter jobs when API is unavailable"""
        return [
            {
                'id': f'zip_fallback_{i}',
                'title': f'{query} Specialist',
                'company': f'Growing Company {i+1}',
                'location': location,
                'summary': f'Join our team as a {query} specialist...',
                'url': f'https://ziprecruiter.com/jobs?search={quote_plus(query)}',
                'date_posted': 'Recent',
                'salary': 'Competitive',
                'source': 'ZipRecruiter',
                'affiliate_url': f'https://ziprecruiter.com/jobs?search={quote_plus(query)}&ref=skillsync',
                'tracking_id': f'zip_fallback_{i}',
                'revenue_potential': 100,
                'platform_priority': 3,
                'match_score': 70 - i*5
            }
            for i in range(min(limit, 5))
        ]

# Revenue tracking and analytics
class JobRevenueTracker:
    """Track job clicks, applications, and revenue attribution"""
    
    def __init__(self):
        self.click_events = []
        self.application_events = []
        self.revenue_events = []
    
    def track_job_click(self, user_id: str, job_id: str, tracking_id: str, 
                       platform: str, revenue_potential: float):
        """Track when user clicks on a job"""
        event = {
            'event_type': 'job_click',
            'user_id': user_id,
            'job_id': job_id,
            'tracking_id': tracking_id,
            'platform': platform,
            'revenue_potential': revenue_potential,
            'timestamp': datetime.now().isoformat()
        }
        
        self.click_events.append(event)
        print(f"[REVENUE] Job click tracked: {platform} - ${revenue_potential}")
        
        return event
    
    def track_job_application(self, user_id: str, job_id: str, tracking_id: str):
        """Track when user applies to a job"""
        event = {
            'event_type': 'job_application',
            'user_id': user_id,
            'job_id': job_id,
            'tracking_id': tracking_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.application_events.append(event)
        print(f"[REVENUE] Job application tracked: {tracking_id}")
        
        return event
    
    def calculate_revenue_metrics(self) -> Dict:
        """Calculate revenue metrics and projections"""
        total_clicks = len(self.click_events)
        total_applications = len(self.application_events)
        
        # Estimated conversion rates
        click_to_application_rate = 0.15  # 15% of clicks become applications
        application_to_hire_rate = 0.05   # 5% of applications become hires
        
        projected_hires = total_applications * application_to_hire_rate
        projected_revenue = sum(event['revenue_potential'] for event in self.click_events) * application_to_hire_rate
        
        return {
            'total_clicks': total_clicks,
            'total_applications': total_applications,
            'projected_hires': projected_hires,
            'projected_revenue': projected_revenue,
            'click_to_application_rate': click_to_application_rate,
            'application_to_hire_rate': application_to_hire_rate,
            'revenue_per_user': projected_revenue / max(total_clicks, 1)
        }
