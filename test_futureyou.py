#!/usr/bin/env python3
"""
Unit Tests for FutureYou AI Agents System
"""

import unittest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from dataclasses import asdict

# Import the classes we want to test
from futureyou import (
    InputValidator, DecisionDNA, FutureScenario, Session,
    ProfilerAgent, SimulatorAgent, AnalyzerAgent, AdvisorAgent,
    TrackerAgent, MemoryBank, FutureYouOrchestrator
)

class TestInputValidator(unittest.TestCase):
    """Test input validation functionality"""
    
    def test_validate_user_profile_valid(self):
        """Test valid user profile validation"""
        valid_profile = {
            'user_id': 'test_user',
            'age': 25,
            'current_role': 'Engineer',
            'skills': ['Python', 'AI'],
            'interests': ['Tech'],
            'life_goals': ['Success'],
            'past_decisions': ['Choice A']
        }
        
        result = InputValidator.validate_user_profile(valid_profile)
        self.assertEqual(result['user_id'], 'test_user')
        self.assertEqual(result['age'], 25)
    
    def test_validate_user_profile_missing_required(self):
        """Test validation with missing required fields"""
        invalid_profile = {
            'age': 25,
            'current_role': 'Engineer'
        }
        
        with self.assertRaises(ValueError) as context:
            InputValidator.validate_user_profile(invalid_profile)
        self.assertIn('Missing required field: user_id', str(context.exception))
    
    def test_validate_user_profile_invalid_age(self):
        """Test validation with invalid age"""
        invalid_profile = {
            'user_id': 'test_user',
            'age': 150,  # Invalid age
            'current_role': 'Engineer'
        }
        
        with self.assertRaises(ValueError) as context:
            InputValidator.validate_user_profile(invalid_profile)
        self.assertIn('Age must be an integer between 16 and 100', str(context.exception))
    
    def test_validate_decision_valid(self):
        """Test valid decision validation"""
        valid_decision = "Should I change my career path to focus on AI?"
        result = InputValidator.validate_decision(valid_decision)
        self.assertEqual(result, valid_decision)
    
    def test_validate_decision_too_short(self):
        """Test decision validation with too short text"""
        short_decision = "Yes?"
        
        with self.assertRaises(ValueError) as context:
            InputValidator.validate_decision(short_decision)
        self.assertIn('Decision must be at least 10 characters long', str(context.exception))
    
    def test_validate_timelines_valid(self):
        """Test valid timeline validation"""
        valid_timelines = ['1yr', '3yr', '5yr']
        result = InputValidator.validate_timelines(valid_timelines)
        self.assertEqual(result, valid_timelines)
    
    def test_validate_timelines_invalid(self):
        """Test timeline validation with invalid timeline"""
        invalid_timelines = ['1yr', '10yr']  # 10yr is not valid
        
        with self.assertRaises(ValueError) as context:
            InputValidator.validate_timelines(invalid_timelines)
        self.assertIn('Invalid timeline: 10yr', str(context.exception))

class TestDataClasses(unittest.TestCase):
    """Test data class functionality"""
    
    def test_decision_dna_creation(self):
        """Test DecisionDNA creation"""
        dna = DecisionDNA(
            risk_tolerance=0.7,
            time_horizon_preference='medium',
            value_priorities=['career', 'wealth'],
            decision_patterns={'style': 'analytical'},
            emotional_drivers=['achievement']
        )
        
        self.assertEqual(dna.risk_tolerance, 0.7)
        self.assertEqual(dna.time_horizon_preference, 'medium')
        self.assertIn('career', dna.value_priorities)
    
    def test_future_scenario_creation(self):
        """Test FutureScenario creation"""
        scenario = FutureScenario(
            scenario_id='1yr_0',
            timeline='1yr',
            decision_path='Take the job',
            outcomes={'career': 'Growth'},
            probability=0.8,
            key_events=['Start job'],
            risks=['Market downturn'],
            opportunities=['Skill development']
        )
        
        self.assertEqual(scenario.scenario_id, '1yr_0')
        self.assertEqual(scenario.probability, 0.8)
        self.assertIn('Growth', scenario.outcomes.values())

class TestMemoryBank(unittest.TestCase):
    """Test memory bank functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.memory = MemoryBank()
        self.test_session = Session(
            session_id='test_session',
            user_profile={'user_id': 'test_user'},
            decision_dna=None,
            scenarios=[],
            conversation_history=[],
            created_at='2024-01-01T00:00:00'
        )
    
    def test_save_and_get_session(self):
        """Test saving and retrieving sessions"""
        self.memory.save_session(self.test_session)
        retrieved = self.memory.get_session('test_session')
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.session_id, 'test_session')
    
    def test_get_nonexistent_session(self):
        """Test retrieving non-existent session"""
        result = self.memory.get_session('nonexistent')
        self.assertIsNone(result)
    
    def test_get_user_history(self):
        """Test getting user history"""
        self.memory.save_session(self.test_session)
        history = self.memory.get_user_history('test_user')
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].session_id, 'test_session')

class TestTrackerAgent(unittest.TestCase):
    """Test tracker agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tracker = TrackerAgent()
    
    def test_log_decision(self):
        """Test logging decisions"""
        self.tracker.log_decision(
            decision='Test decision',
            chosen_path='Path A',
            reasoning='Best option'
        )
        
        history = self.tracker.get_decision_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['decision'], 'Test decision')
        self.assertEqual(history[0]['chosen_path'], 'Path A')
    
    def test_multiple_decisions(self):
        """Test logging multiple decisions"""
        for i in range(3):
            self.tracker.log_decision(
                decision=f'Decision {i}',
                chosen_path=f'Path {i}',
                reasoning=f'Reason {i}'
            )
        
        history = self.tracker.get_decision_history()
        self.assertEqual(len(history), 3)

class TestAgentsWithMocks(unittest.TestCase):
    """Test agents with mocked Gemini API calls"""
    
    def setUp(self):
        """Set up test fixtures with mocks"""
        self.mock_model = Mock()
        
    @patch('futureyou.genai.GenerativeModel')
    def test_profiler_agent_initialization(self, mock_genai):
        """Test ProfilerAgent initialization"""
        mock_genai.return_value = self.mock_model
        
        profiler = ProfilerAgent()
        self.assertIsNotNone(profiler.model)
        mock_genai.assert_called_once()
    
    @patch('futureyou.genai.GenerativeModel')
    def test_simulator_agent_initialization(self, mock_genai):
        """Test SimulatorAgent initialization"""
        mock_genai.return_value = self.mock_model
        
        simulator = SimulatorAgent()
        self.assertIsNotNone(simulator.model)
        mock_genai.assert_called_once()
    
    @patch('futureyou.genai.GenerativeModel')
    def test_analyzer_agent_initialization(self, mock_genai):
        """Test AnalyzerAgent initialization"""
        mock_genai.return_value = self.mock_model
        
        analyzer = AnalyzerAgent()
        self.assertIsNotNone(analyzer.model)
        mock_genai.assert_called_once()
    
    @patch('futureyou.genai.GenerativeModel')
    def test_advisor_agent_initialization(self, mock_genai):
        """Test AdvisorAgent initialization"""
        mock_genai.return_value = self.mock_model
        
        advisor = AdvisorAgent()
        self.assertIsNotNone(advisor.model)
        mock_genai.assert_called_once()

class TestOrchestratorIntegration(unittest.TestCase):
    """Test orchestrator integration"""
    
    @patch('futureyou.genai.GenerativeModel')
    def setUp(self, mock_genai):
        """Set up test fixtures"""
        mock_genai.return_value = Mock()
        self.orchestrator = FutureYouOrchestrator()
        
        self.test_user_data = {
            'user_id': 'test_user',
            'age': 28,
            'current_role': 'Engineer',
            'skills': ['Python'],
            'interests': ['AI'],
            'life_goals': ['Success'],
            'past_decisions': []
        }
    
    def test_create_session(self):
        """Test session creation"""
        session = self.orchestrator.create_session(self.test_user_data)
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.user_profile['user_id'], 'test_user')
        self.assertIsNone(session.decision_dna)
        self.assertEqual(len(session.scenarios), 0)

class TestFileOperations(unittest.TestCase):
    """Test file operations and JSON handling"""
    
    def test_json_input_validation(self):
        """Test JSON input file validation"""
        valid_input = {
            "user_profile": {
                "user_id": "test_user",
                "age": 25,
                "current_role": "Engineer"
            },
            "decision": "Should I change jobs?",
            "timelines": ["1yr", "3yr"],
            "generate_visuals": False
        }
        
        # Test that valid input doesn't raise errors
        try:
            InputValidator.validate_user_profile(valid_input["user_profile"])
            InputValidator.validate_decision(valid_input["decision"])
            InputValidator.validate_timelines(valid_input["timelines"])
        except ValueError:
            self.fail("Valid input should not raise ValueError")
    
    def test_json_serialization(self):
        """Test JSON serialization of data classes"""
        dna = DecisionDNA(
            risk_tolerance=0.5,
            time_horizon_preference='medium',
            value_priorities=['career'],
            decision_patterns={'style': 'analytical'},
            emotional_drivers=['achievement']
        )
        
        # Test that asdict works correctly
        dna_dict = asdict(dna)
        self.assertIsInstance(dna_dict, dict)
        self.assertEqual(dna_dict['risk_tolerance'], 0.5)
        
        # Test JSON serialization
        json_str = json.dumps(dna_dict)
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        self.assertEqual(loaded_dict['risk_tolerance'], 0.5)

class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def test_empty_input_handling(self):
        """Test handling of empty inputs"""
        with self.assertRaises(ValueError):
            InputValidator.validate_decision("")
        
        with self.assertRaises(ValueError):
            InputValidator.validate_decision(None)
        
        with self.assertRaises(ValueError):
            InputValidator.validate_timelines([])
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        with self.assertRaises(ValueError):
            InputValidator.validate_user_profile("not a dict")
        
        with self.assertRaises(ValueError):
            InputValidator.validate_decision(123)  # Not a string
        
        with self.assertRaises(ValueError):
            InputValidator.validate_timelines("not a list")

if __name__ == '__main__':
    # Set up test environment
    os.environ['GEMINI_API_KEY'] = 'test_key_for_testing'
    
    # Run tests
    unittest.main(verbosity=2)