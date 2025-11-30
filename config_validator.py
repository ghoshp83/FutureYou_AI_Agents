#!/usr/bin/env python3
"""
Configuration Validator for FutureYou
Validates system configuration and environment setup
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates system configuration and environment"""
    
    @staticmethod
    def validate_environment() -> Dict[str, Any]:
        """Validate environment variables and system setup"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            validation_results['valid'] = False
            validation_results['errors'].append(
                "GEMINI_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        elif api_key == 'your_gemini_api_key_here':
            validation_results['valid'] = False
            validation_results['errors'].append(
                "GEMINI_API_KEY appears to be the default placeholder. "
                "Please set your actual API key."
            )
        elif len(api_key) < 20:
            validation_results['warnings'].append(
                "GEMINI_API_KEY seems unusually short. Please verify it's correct."
            )
        else:
            validation_results['info'].append("✓ GEMINI_API_KEY found and appears valid")
        
        # Check .env file
        if os.path.exists('.env'):
            validation_results['info'].append("✓ .env file found")
        else:
            validation_results['warnings'].append(
                ".env file not found. Consider creating one from .env.example"
            )
        
        # Check required directories
        required_dirs = ['results', 'results/outputs', 'results/visualizations']
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    validation_results['info'].append(f"✓ Created directory: {dir_path}")
                except Exception as e:
                    validation_results['errors'].append(f"Cannot create directory {dir_path}: {e}")
            else:
                validation_results['info'].append(f"✓ Directory exists: {dir_path}")
        
        return validation_results
    
    @staticmethod
    def validate_input_file(file_path: str = 'futureyou_input.json') -> Dict[str, Any]:
        """Validate input JSON file"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        # Check if file exists
        if not os.path.exists(file_path):
            validation_results['valid'] = False
            validation_results['errors'].append(f"Input file {file_path} not found")
            return validation_results
        
        try:
            # Load and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            validation_results['info'].append(f"✓ {file_path} loaded successfully")
            
            # Validate structure
            required_keys = ['user_profile', 'decision']
            for key in required_keys:
                if key not in data:
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Missing required key: {key}")
            
            # Validate user_profile
            if 'user_profile' in data:
                profile = data['user_profile']
                required_profile_keys = ['user_id', 'age', 'current_role']
                
                for key in required_profile_keys:
                    if key not in profile:
                        validation_results['valid'] = False
                        validation_results['errors'].append(f"Missing required profile key: {key}")
                
                # Validate age
                if 'age' in profile:
                    age = profile['age']
                    if not isinstance(age, int) or age < 16 or age > 100:
                        validation_results['valid'] = False
                        validation_results['errors'].append("Age must be an integer between 16 and 100")
                
                # Check optional fields
                optional_fields = ['skills', 'interests', 'life_goals', 'past_decisions']
                for field in optional_fields:
                    if field not in profile:
                        validation_results['warnings'].append(f"Optional field missing: {field}")
                    elif not isinstance(profile[field], list):
                        validation_results['errors'].append(f"{field} must be a list")
            
            # Validate decision
            if 'decision' in data:
                decision = data['decision']
                if not isinstance(decision, str) or len(decision.strip()) < 10:
                    validation_results['valid'] = False
                    validation_results['errors'].append("Decision must be a string with at least 10 characters")
            
            # Validate timelines
            if 'timelines' in data:
                timelines = data['timelines']
                valid_timelines = ['1yr', '3yr', '5yr']
                if not isinstance(timelines, list):
                    validation_results['errors'].append("Timelines must be a list")
                else:
                    for timeline in timelines:
                        if timeline not in valid_timelines:
                            validation_results['errors'].append(f"Invalid timeline: {timeline}")
            else:
                validation_results['info'].append("Using default timelines: ['1yr', '3yr', '5yr']")
            
            # Check generate_visuals
            if 'generate_visuals' in data:
                if not isinstance(data['generate_visuals'], bool):
                    validation_results['warnings'].append("generate_visuals should be a boolean")
            
        except json.JSONDecodeError as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Error reading {file_path}: {e}")
        
        return validation_results
    
    @staticmethod
    def validate_dependencies() -> Dict[str, Any]:
        """Validate required Python packages"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': []
        }
        
        required_packages = {
            'google.generativeai': 'google-generativeai>=0.3.0',
            'tenacity': 'tenacity>=8.0.0',
            'dotenv': 'python-dotenv>=1.0.0',
            'PIL': 'Pillow>=10.0.0'
        }
        
        for import_name, package_name in required_packages.items():
            try:
                if import_name == 'dotenv':
                    from dotenv import load_dotenv
                elif import_name == 'PIL':
                    from PIL import Image
                elif import_name == 'google.generativeai':
                    import google.generativeai as genai
                elif import_name == 'tenacity':
                    import tenacity
                
                validation_results['info'].append(f"✓ {package_name} available")
                
            except ImportError:
                validation_results['valid'] = False
                validation_results['errors'].append(f"Missing package: {package_name}")
        
        return validation_results
    
    @staticmethod
    def run_full_validation() -> Dict[str, Any]:
        """Run complete system validation"""
        print("🔍 Running FutureYou System Validation...")
        print("=" * 50)
        
        all_results = {
            'overall_valid': True,
            'environment': {},
            'dependencies': {},
            'input_file': {}
        }
        
        # Validate environment
        print("\n📋 Checking Environment...")
        env_results = ConfigValidator.validate_environment()
        all_results['environment'] = env_results
        if not env_results['valid']:
            all_results['overall_valid'] = False
        
        # Print environment results
        for error in env_results['errors']:
            print(f"❌ {error}")
        for warning in env_results['warnings']:
            print(f"⚠️  {warning}")
        for info in env_results['info']:
            print(f"   {info}")
        
        # Validate dependencies
        print("\n📦 Checking Dependencies...")
        dep_results = ConfigValidator.validate_dependencies()
        all_results['dependencies'] = dep_results
        if not dep_results['valid']:
            all_results['overall_valid'] = False
        
        # Print dependency results
        for error in dep_results['errors']:
            print(f"❌ {error}")
        for warning in dep_results['warnings']:
            print(f"⚠️  {warning}")
        for info in dep_results['info']:
            print(f"   {info}")
        
        # Validate input file
        print("\n📄 Checking Input File...")
        input_results = ConfigValidator.validate_input_file()
        all_results['input_file'] = input_results
        if not input_results['valid']:
            all_results['overall_valid'] = False
        
        # Print input file results
        for error in input_results['errors']:
            print(f"❌ {error}")
        for warning in input_results['warnings']:
            print(f"⚠️  {warning}")
        for info in input_results['info']:
            print(f"   {info}")
        
        # Final status
        print("\n" + "=" * 50)
        if all_results['overall_valid']:
            print("✅ System validation PASSED - Ready to run!")
        else:
            print("❌ System validation FAILED - Please fix errors above")
        print("=" * 50)
        
        return all_results

def main():
    """Run validation as standalone script"""
    results = ConfigValidator.run_full_validation()
    
    if not results['overall_valid']:
        print("\n🔧 Quick fixes:")
        if not results['environment']['valid']:
            print("1. Copy .env.example to .env and add your GEMINI_API_KEY")
        if not results['dependencies']['valid']:
            print("2. Run: pip install -r requirements.txt")
        if not results['input_file']['valid']:
            print("3. Create futureyou_input.json from futureyou_input.json.example")
        
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())