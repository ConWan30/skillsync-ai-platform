#!/usr/bin/env python3
"""
SkillSync AI System Validation Script
Comprehensive testing of all systems, endpoints, and functionality
"""

import sys
import requests
import json
from datetime import datetime
import os

class SkillSyncValidator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = []
        
    def log_test(self, test_name, status, message, details=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {message}")
        
    def test_basic_routes(self):
        """Test all basic Flask routes"""
        routes = [
            '/', '/dashboard', '/career-paths', '/market-intelligence',
            '/tools', '/ai-agent', '/community', '/mentorship', 
            '/events', '/analytics', '/health'
        ]
        
        passed = 0
        total = len(routes)
        
        for route in routes:
            try:
                response = requests.get(f"{self.base_url}{route}", timeout=10)
                if response.status_code == 200:
                    self.log_test(f"Route {route}", "PASS", "Route accessible")
                    passed += 1
                else:
                    self.log_test(f"Route {route}", "FAIL", f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Route {route}", "FAIL", f"Connection error: {str(e)}")
        
        self.log_test("Basic Routes Summary", "PASS" if passed == total else "WARN", 
                     f"{passed}/{total} routes working")
        
    def test_api_endpoints(self):
        """Test API endpoints"""
        api_tests = [
            {
                'endpoint': '/api/system/status',
                'method': 'GET',
                'expected_keys': ['timestamp', 'overall_status', 'components']
            },
            {
                'endpoint': '/api/test/all-systems',
                'method': 'POST',
                'data': {},
                'expected_keys': ['timestamp', 'tests']
            },
            {
                'endpoint': '/api/ai/assess-skills',
                'method': 'POST',
                'data': {'skills_description': 'Python, JavaScript, 2 years experience'},
                'expected_keys': ['success']
            }
        ]
        
        for test in api_tests:
            try:
                if test['method'] == 'GET':
                    response = requests.get(f"{self.base_url}{test['endpoint']}", timeout=10)
                else:
                    response = requests.post(
                        f"{self.base_url}{test['endpoint']}", 
                        json=test.get('data', {}),
                        timeout=10
                    )
                
                if response.status_code == 200:
                    data = response.json()
                    missing_keys = [key for key in test['expected_keys'] if key not in data]
                    
                    if not missing_keys:
                        self.log_test(f"API {test['endpoint']}", "PASS", "Endpoint working correctly")
                    else:
                        self.log_test(f"API {test['endpoint']}", "WARN", 
                                    f"Missing keys: {missing_keys}", data)
                else:
                    self.log_test(f"API {test['endpoint']}", "FAIL", 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"API {test['endpoint']}", "FAIL", f"Request error: {str(e)}")
    
    def test_advanced_features(self):
        """Test advanced MCP and A2A features"""
        advanced_tests = [
            {
                'endpoint': '/api/mcp/salary-intelligence',
                'data': {'job_title': 'Software Developer', 'location': 'Remote'},
                'expected_fallback': True
            },
            {
                'endpoint': '/api/a2a/multi-perspective-analysis',
                'data': {'career_data': {'skills': ['Python'], 'experience': 2}},
                'expected_fallback': True
            }
        ]
        
        for test in advanced_tests:
            try:
                response = requests.post(
                    f"{self.base_url}{test['endpoint']}", 
                    json=test['data'],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        self.log_test(f"Advanced {test['endpoint']}", "PASS", 
                                    "Advanced feature fully functional")
                    elif 'fallback_data' in data or 'error' in data:
                        self.log_test(f"Advanced {test['endpoint']}", "WARN", 
                                    "Feature has graceful fallback", data)
                    else:
                        self.log_test(f"Advanced {test['endpoint']}", "FAIL", 
                                    "Unexpected response format", data)
                else:
                    self.log_test(f"Advanced {test['endpoint']}", "FAIL", 
                                f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Advanced {test['endpoint']}", "FAIL", f"Request error: {str(e)}")
    
    def test_database_functionality(self):
        """Test database through API"""
        try:
            # Test user creation
            test_user = {
                'username': f'test_user_{datetime.now().timestamp()}',
                'email': f'test_{datetime.now().timestamp()}@example.com'
            }
            
            response = requests.post(f"{self.base_url}/api/users", json=test_user, timeout=10)
            
            if response.status_code == 201:
                self.log_test("Database User Creation", "PASS", "User creation working")
                
                # Test user data retrieval
                user_data = response.json()
                user_id = user_data.get('id')
                
                if user_id:
                    assess_response = requests.get(
                        f"{self.base_url}/api/users/{user_id}/assessments", 
                        timeout=10
                    )
                    
                    if assess_response.status_code == 200:
                        self.log_test("Database Read Operations", "PASS", "Data retrieval working")
                    else:
                        self.log_test("Database Read Operations", "WARN", 
                                    f"Read status: {assess_response.status_code}")
                        
            elif response.status_code == 409:
                self.log_test("Database User Creation", "WARN", "User already exists (database working)")
            else:
                self.log_test("Database User Creation", "FAIL", 
                            f"Creation failed: {response.status_code}")
                
        except Exception as e:
            self.log_test("Database Functionality", "FAIL", f"Database error: {str(e)}")
    
    def run_all_tests(self):
        """Run comprehensive system validation"""
        print("🚀 Starting SkillSync AI System Validation")
        print("=" * 50)
        
        # Test basic functionality
        print("\n📋 Testing Basic Routes...")
        self.test_basic_routes()
        
        print("\n🔌 Testing API Endpoints...")
        self.test_api_endpoints()
        
        print("\n🧠 Testing Advanced Features...")
        self.test_advanced_features()
        
        print("\n💾 Testing Database Functionality...")
        self.test_database_functionality()
        
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        warned = len([r for r in self.test_results if r['status'] == 'WARN'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total Tests: {total}")
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 System Status: EXCELLENT - Ready for production!")
        elif success_rate >= 60:
            print("\n👍 System Status: GOOD - Minor issues to address")
        else:
            print("\n⚠️  System Status: NEEDS ATTENTION - Several issues found")
        
        # Save detailed results
        self.save_results()
        
    def save_results(self):
        """Save detailed test results"""
        try:
            with open('validation_results.json', 'w') as f:
                json.dump({
                    'validation_timestamp': datetime.now().isoformat(),
                    'test_results': self.test_results,
                    'summary': {
                        'total_tests': len(self.test_results),
                        'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
                        'warned': len([r for r in self.test_results if r['status'] == 'WARN']),
                        'failed': len([r for r in self.test_results if r['status'] == 'FAIL'])
                    }
                }, f, indent=2)
            print(f"\n💾 Detailed results saved to validation_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate SkillSync AI System')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL for the application (default: http://localhost:5000)')
    
    args = parser.parse_args()
    
    validator = SkillSyncValidator(args.url)
    validator.run_all_tests()

if __name__ == '__main__':
    main()