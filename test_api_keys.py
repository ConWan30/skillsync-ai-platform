#!/usr/bin/env python3
"""
SkillSync AI - API Key Testing Script
Test all API integrations to verify they're working with real data
"""

import requests
import json
import os
from datetime import datetime

class APIKeyTester:
    def __init__(self, base_url="https://skillsync-ai-platform-production.up.railway.app"):
        self.base_url = base_url
        self.results = []
        
    def log_test(self, test_name, success, details, response_data=None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_preview': str(response_data)[:200] + "..." if response_data else None
        }
        self.results.append(result)
        
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_system_status(self):
        """Test overall system status"""
        try:
            response = requests.get(f"{self.base_url}/api/system/status", timeout=10)
            data = response.json()
            
            # Check API configurations
            xai_status = data['components']['xai_api']['status']
            mcp_status = data['components']['mcp_system']['status']
            
            self.log_test("System Status", True, f"xAI: {xai_status}, MCP: {mcp_status}", data)
            return data
            
        except Exception as e:
            self.log_test("System Status", False, f"Failed: {str(e)}")
            return None
    
    def test_xai_integration(self):
        """Test xAI API integration"""
        test_data = {
            "skills_description": "Senior Python developer with 7 years experience in machine learning, Django, and cloud deployment on AWS"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/assess-skills",
                json=test_data,
                timeout=15
            )
            data = response.json()
            
            # Check if we got real AI analysis or fallback
            if 'assessment' in data and 'error' not in data['assessment']:
                content = data['assessment'].get('content', '')
                if 'Demo Mode' in content or 'API key' in content:
                    self.log_test("xAI Integration", False, "Using fallback/demo mode", data)
                else:
                    self.log_test("xAI Integration", True, "Real AI analysis received", data)
            else:
                error_msg = data.get('assessment', {}).get('error', 'Unknown error')
                self.log_test("xAI Integration", False, f"Error: {error_msg}", data)
                
        except Exception as e:
            self.log_test("xAI Integration", False, f"Request failed: {str(e)}")
    
    def test_brave_api_integration(self):
        """Test Brave API integration through MCP"""
        test_data = {
            "job_title": "Machine Learning Engineer",
            "location": "Seattle"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/mcp/salary-intelligence",
                json=test_data,
                timeout=15
            )
            data = response.json()
            
            # Check if we got real data
            if data.get('success') and 'salary_intelligence' in data:
                salary_data = data['salary_intelligence']
                data_sources = salary_data.get('data_sources', 0)
                
                if data_sources > 0:
                    self.log_test("Brave API Integration", True, f"Real data: {data_sources} sources", salary_data)
                else:
                    self.log_test("Brave API Integration", False, "No real data sources found", salary_data)
            else:
                self.log_test("Brave API Integration", False, "API call failed", data)
                
        except Exception as e:
            self.log_test("Brave API Integration", False, f"Request failed: {str(e)}")
    
    def test_revolutionary_ai_radar(self):
        """Test AI Opportunity Radar with different profiles"""
        profiles = [
            {
                "name": "Junior Developer",
                "data": {
                    "skills": ["JavaScript", "React", "Node.js"],
                    "experience_years": 2,
                    "target_salary": 80000,
                    "location": "Remote"
                }
            },
            {
                "name": "Senior Engineer", 
                "data": {
                    "skills": ["Python", "Machine Learning", "AWS", "Docker"],
                    "experience_years": 8,
                    "target_salary": 160000,
                    "location": "San Francisco"
                }
            }
        ]
        
        for profile in profiles:
            try:
                response = requests.post(
                    f"{self.base_url}/api/ai/opportunity-radar",
                    json=profile["data"],
                    timeout=15
                )
                data = response.json()
                
                if data.get('success'):
                    opportunities = data.get('opportunities', [])
                    market_intel = data.get('market_intelligence', {})
                    
                    # Check if results vary based on input
                    location_match = any(profile["data"]["location"].lower() in str(opp).lower() 
                                       for opp in opportunities)
                    
                    self.log_test(
                        f"AI Radar - {profile['name']}", 
                        True, 
                        f"Got {len(opportunities)} opportunities, location aware: {location_match}",
                        {'opportunities_count': len(opportunities), 'location': market_intel.get('location')}
                    )
                else:
                    self.log_test(f"AI Radar - {profile['name']}", False, "API call failed", data)
                    
            except Exception as e:
                self.log_test(f"AI Radar - {profile['name']}", False, f"Request failed: {str(e)}")
    
    def test_career_pivot_ai(self):
        """Test AI Career Pivot Pathfinder"""
        test_data = {
            "current_role": "Software Developer",
            "target_career": "Data Scientist", 
            "skills": ["Python", "SQL", "Git"],
            "experience_years": 4,
            "current_salary": 95000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/ai/career-pivot-pathfinder",
                json=test_data,
                timeout=15
            )
            data = response.json()
            
            if data.get('success'):
                pivot_path = data.get('pivot_path', {})
                success_prob = pivot_path.get('success_probability', 0)
                bridge_roles = pivot_path.get('bridge_roles', [])
                
                self.log_test(
                    "AI Career Pivot", 
                    True, 
                    f"Success prob: {success_prob:.1%}, Bridge roles: {len(bridge_roles)}",
                    {'success_probability': success_prob, 'bridge_roles_count': len(bridge_roles)}
                )
            else:
                self.log_test("AI Career Pivot", False, "API call failed", data)
                
        except Exception as e:
            self.log_test("AI Career Pivot", False, f"Request failed: {str(e)}")
    
    def test_frontend_button_endpoints(self):
        """Test common frontend button endpoints"""
        button_tests = [
            {"endpoint": "/analytics", "name": "Analytics Page"},
            {"endpoint": "/events", "name": "Events Page"},
            {"endpoint": "/ai-opportunity-radar", "name": "AI Opportunity Radar Page"},
            {"endpoint": "/ai-career-pivot", "name": "AI Career Pivot Page"}
        ]
        
        for test in button_tests:
            try:
                response = requests.get(f"{self.base_url}{test['endpoint']}", timeout=10)
                
                if response.status_code == 200:
                    # Check if it's actually loading the page (not just returning 200)
                    content = response.text
                    if len(content) > 1000 and '<html' in content.lower():
                        self.log_test(test['name'], True, f"Page loads successfully ({len(content)} chars)")
                    else:
                        self.log_test(test['name'], False, f"Page too small or invalid ({len(content)} chars)")
                else:
                    self.log_test(test['name'], False, f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_test(test['name'], False, f"Request failed: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE API TESTING REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")  
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nISSUES FOUND:")
        for result in self.results:
            if not result['success']:
                print(f"   [FAIL] {result['test']}: {result['details']}")
        
        print("\nRECOMMENDATIONS:")
        
        # Check for specific issues
        xai_failed = any('xAI' in r['test'] and not r['success'] for r in self.results)
        brave_failed = any('Brave' in r['test'] and not r['success'] for r in self.results)
        
        if xai_failed:
            print("   1. xAI API Key Issues:")
            print("      - Verify XAI_API_KEY is set in Railway variables")
            print("      - Check if API key is valid at https://console.x.ai")
            print("      - Consider increasing timeout or using different model")
        
        if brave_failed:
            print("   2. Brave API Key Issues:")
            print("      - Verify BRAVE_API_KEY is set in Railway variables") 
            print("      - Check API key is valid at https://api.search.brave.com")
            print("      - Ensure sufficient API quota")
        
        # Save detailed results
        self.save_detailed_results()
    
    def save_detailed_results(self):
        """Save detailed test results to file"""
        try:
            report = {
                'test_timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_tests': len(self.results),
                    'passed': len([r for r in self.results if r['success']]),
                    'failed': len([r for r in self.results if not r['success']])
                },
                'detailed_results': self.results
            }
            
            with open('api_test_results.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\nDetailed results saved to: api_test_results.json")
            
        except Exception as e:
            print(f"\nCould not save results: {e}")

def main():
    """Run comprehensive API testing"""
    print("Starting Comprehensive API Key Testing...")
    print("="*60)
    
    tester = APIKeyTester()
    
    # Run all tests
    print("\n1. Testing System Status...")
    tester.test_system_status()
    
    print("\n2. Testing xAI Integration...")
    tester.test_xai_integration()
    
    print("\n3. Testing Brave API Integration...")
    tester.test_brave_api_integration()
    
    print("\n4. Testing AI Opportunity Radar...")
    tester.test_revolutionary_ai_radar()
    
    print("\n5. Testing AI Career Pivot...")
    tester.test_career_pivot_ai()
    
    print("\n6. Testing Frontend Pages...")
    tester.test_frontend_button_endpoints()
    
    # Generate final report
    tester.generate_report()

if __name__ == "__main__":
    main()