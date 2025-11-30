#!/usr/bin/env python3
"""
FutureYou: Personal Future Simulator
A multi-agent system that simulates multiple future scenarios to help users make better life decisions.

Author: FutureYou Team
Version: 1.0.0
License: MIT
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('futureyou.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Validate API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")

# Initialize Gemini with error handling
try:
    genai.configure(api_key=api_key)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise

@dataclass
class DecisionDNA:
    """Unique decision-making pattern extracted from user's history"""
    risk_tolerance: float  # 0-1
    time_horizon_preference: str  # short/medium/long
    value_priorities: List[str]  # career, family, health, wealth, freedom
    decision_patterns: Dict[str, Any]  # past decision analysis
    emotional_drivers: List[str]
    
@dataclass
class FutureScenario:
    """A simulated future scenario"""
    scenario_id: str
    timeline: str  # 1yr, 3yr, 5yr
    decision_path: str
    outcomes: Dict[str, Any]
    probability: float
    key_events: List[str]
    risks: List[str]
    opportunities: List[str]

@dataclass
class Session:
    """User session with memory"""
    session_id: str
    user_profile: Dict[str, Any]
    decision_dna: Optional[DecisionDNA]
    scenarios: List[FutureScenario]
    conversation_history: List[Dict[str, str]]
    created_at: str

class MemoryBank:
    """Long-term memory storage for user profiles and decision patterns"""
    def __init__(self):
        self.storage = {}
        
    def save_session(self, session: Session):
        self.storage[session.session_id] = asdict(session)
        
    def get_session(self, session_id: str) -> Optional[Session]:
        data = self.storage.get(session_id)
        return Session(**data) if data else None
        
    def get_user_history(self, user_id: str) -> List[Session]:
        return [Session(**s) for s in self.storage.values() 
                if s.get('user_profile', {}).get('user_id') == user_id]

class InputValidator:
    """Validates user inputs and configuration"""
    
    @staticmethod
    def validate_user_profile(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user profile data"""
        required_fields = ['user_id', 'age', 'current_role']
        
        for field in required_fields:
            if field not in user_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate age
        age = user_data.get('age')
        if not isinstance(age, int) or age < 16 or age > 100:
            raise ValueError("Age must be an integer between 16 and 100")
        
        # Ensure lists exist
        list_fields = ['skills', 'interests', 'life_goals', 'past_decisions']
        for field in list_fields:
            if field not in user_data:
                user_data[field] = []
            elif not isinstance(user_data[field], list):
                raise ValueError(f"{field} must be a list")
        
        return user_data
    
    @staticmethod
    def validate_decision(decision: str) -> str:
        """Validate decision text"""
        if not decision or not isinstance(decision, str):
            raise ValueError("Decision must be a non-empty string")
        
        if len(decision.strip()) < 10:
            raise ValueError("Decision must be at least 10 characters long")
        
        return decision.strip()
    
    @staticmethod
    def validate_timelines(timelines: List[str]) -> List[str]:
        """Validate timeline list"""
        valid_timelines = ['1yr', '3yr', '5yr']
        
        if not timelines or not isinstance(timelines, list):
            raise ValueError("Timelines must be a non-empty list")
        
        for timeline in timelines:
            if timeline not in valid_timelines:
                raise ValueError(f"Invalid timeline: {timeline}. Must be one of {valid_timelines}")
        
        return timelines

class ProfilerAgent:
    """Analyzes user profile and extracts Decision DNA"""
    def __init__(self, model_name: str = "gemini-3-pro-preview"):
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"ProfilerAgent initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ProfilerAgent: {e}")
            raise
        
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def analyze_profile(self, user_data: Dict[str, Any]) -> DecisionDNA:
        """Extract Decision DNA from user profile"""
        try:
            # Validate input
            validated_data = InputValidator.validate_user_profile(user_data)
            logger.info(f"Analyzing profile for user: {validated_data.get('user_id')}")
            
            prompt = f"""Analyze this user profile and extract their Decision DNA:

User Data: {json.dumps(validated_data, indent=2)}

Extract:
1. Risk tolerance (0-1 scale, float)
2. Time horizon preference (short/medium/long)
3. Top 3 value priorities from: career, family, health, wealth, freedom, creativity, impact
4. Decision patterns (how they typically decide)
5. Emotional drivers (what motivates them)

Return ONLY valid JSON with keys: risk_tolerance, time_horizon_preference, value_priorities, decision_patterns, emotional_drivers

Example format:
{{
  "risk_tolerance": 0.7,
  "time_horizon_preference": "medium",
  "value_priorities": ["career", "wealth", "freedom"],
  "decision_patterns": {{"style": "analytical", "speed": "deliberate"}},
  "emotional_drivers": ["achievement", "security"]
}}"""
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Clean and parse JSON
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            result = json.loads(clean_text)
            
            # Validate result structure
            required_keys = ['risk_tolerance', 'time_horizon_preference', 'value_priorities', 'decision_patterns', 'emotional_drivers']
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"Missing key in DNA analysis: {key}")
            
            # Validate risk tolerance
            if not isinstance(result['risk_tolerance'], (int, float)) or not 0 <= result['risk_tolerance'] <= 1:
                raise ValueError("Risk tolerance must be a number between 0 and 1")
            
            logger.info(f"Decision DNA extracted successfully for user: {validated_data.get('user_id')}")
            
            return DecisionDNA(
                risk_tolerance=float(result['risk_tolerance']),
                time_horizon_preference=result['time_horizon_preference'],
                value_priorities=result['value_priorities'],
                decision_patterns=result['decision_patterns'],
                emotional_drivers=result['emotional_drivers']
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Raw response: {response.text if response else 'No response'}")
            raise ValueError(f"Invalid JSON response from AI model: {e}")
        except Exception as e:
            logger.error(f"Error in analyze_profile: {e}")
            raise

class SimulatorAgent:
    """Simulates multiple future scenarios based on different decision paths"""
    def __init__(self, model_name: str = "gemini-3-pro-preview"):
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"SimulatorAgent initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize SimulatorAgent: {e}")
            raise
        
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def simulate_futures(self, decision: str, dna: DecisionDNA, timeline: str) -> List[FutureScenario]:
        """Generate 3 different future scenarios for a decision"""
        try:
            # Validate inputs
            validated_decision = InputValidator.validate_decision(decision)
            
            if timeline not in ['1yr', '3yr', '5yr']:
                raise ValueError(f"Invalid timeline: {timeline}")
            
            logger.info(f"Simulating futures for timeline: {timeline}")
            
            prompt = f"""Simulate 3 different future scenarios for this decision:

Decision: {validated_decision}
Timeline: {timeline}
Decision DNA: {asdict(dna)}

For each scenario (optimistic, realistic, pessimistic), provide:
- decision_path: specific actions taken (string)
- outcomes: concrete results in career, finance, relationships, health, happiness (object)
- probability: likelihood 0-1 (float)
- key_events: major milestones (array of strings)
- risks: potential problems (array of strings)
- opportunities: potential gains (array of strings)

Return ONLY valid JSON array with exactly 3 scenarios.

Example format:
[
  {{
    "decision_path": "Take the startup role",
    "outcomes": {{"career": "Senior role", "finance": "Equity growth"}},
    "probability": 0.7,
    "key_events": ["Join startup", "Product launch"],
    "risks": ["Startup failure"],
    "opportunities": ["Equity upside"]
  }}
]"""
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Clean and parse JSON
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            scenarios_data = json.loads(clean_text)
            
            if not isinstance(scenarios_data, list) or len(scenarios_data) != 3:
                raise ValueError(f"Expected 3 scenarios, got {len(scenarios_data) if isinstance(scenarios_data, list) else 'invalid format'}")
            
            scenarios = []
            for i, data in enumerate(scenarios_data):
                # Validate scenario structure
                required_fields = ['decision_path', 'outcomes', 'probability', 'key_events', 'risks', 'opportunities']
                for field in required_fields:
                    if field not in data:
                        raise ValueError(f"Missing field in scenario {i}: {field}")
                
                # Validate probability
                prob = data['probability']
                if not isinstance(prob, (int, float)) or not 0 <= prob <= 1:
                    raise ValueError(f"Invalid probability in scenario {i}: {prob}")
                
                scenarios.append(FutureScenario(
                    scenario_id=f"{timeline}_{i}",
                    timeline=timeline,
                    decision_path=data['decision_path'],
                    outcomes=data['outcomes'],
                    probability=float(prob),
                    key_events=data['key_events'],
                    risks=data['risks'],
                    opportunities=data['opportunities']
                ))
            
            logger.info(f"Successfully generated {len(scenarios)} scenarios for {timeline}")
            return scenarios
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Raw response: {response.text if response else 'No response'}")
            raise ValueError(f"Invalid JSON response from AI model: {e}")
        except Exception as e:
            logger.error(f"Error in simulate_futures for {timeline}: {e}")
            raise

class AnalyzerAgent:
    """Analyzes scenarios and compares outcomes"""
    def __init__(self, model_name: str = "gemini-3-pro-preview"):
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"AnalyzerAgent initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AnalyzerAgent: {e}")
            raise
        
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def analyze_scenarios(self, scenarios: List[FutureScenario], dna: DecisionDNA) -> Dict[str, Any]:
        """Deep analysis of all scenarios"""
        try:
            if not scenarios:
                raise ValueError("No scenarios provided for analysis")
            
            logger.info(f"Analyzing {len(scenarios)} scenarios")
            
            prompt = f"""Analyze these future scenarios based on the user's Decision DNA:

Scenarios: {json.dumps([asdict(s) for s in scenarios], indent=2)}
Decision DNA: {asdict(dna)}

Provide:
1. best_scenario: which scenario aligns best with user's values (string)
2. risk_analysis: comprehensive risk assessment (string)
3. opportunity_analysis: key opportunities across scenarios (string)
4. alignment_score: how well each scenario matches user's DNA 0-1 (object with scenario_id as keys)
5. trade_offs: what user gains vs loses in each path (string)

Return ONLY valid JSON with these exact keys.

Example format:
{{
  "best_scenario": "1yr_0",
  "risk_analysis": "Main risks include...",
  "opportunity_analysis": "Key opportunities are...",
  "alignment_score": {{"1yr_0": 0.8, "1yr_1": 0.6}},
  "trade_offs": "Higher risk vs higher reward..."
}}"""
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            # Clean and parse JSON
            clean_text = response.text.strip().replace('```json', '').replace('```', '')
            result = json.loads(clean_text)
            
            # Validate result structure
            required_keys = ['best_scenario', 'risk_analysis', 'opportunity_analysis', 'alignment_score', 'trade_offs']
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"Missing key in analysis: {key}")
            
            logger.info("Scenario analysis completed successfully")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {e}")
            logger.error(f"Raw response: {response.text if response else 'No response'}")
            raise ValueError(f"Invalid JSON response from AI model: {e}")
        except Exception as e:
            logger.error(f"Error in analyze_scenarios: {e}")
            raise

class AdvisorAgent:
    """Provides personalized recommendations"""
    def __init__(self, model_name: str = "gemini-3-pro-preview"):
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"AdvisorAgent initialized with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize AdvisorAgent: {e}")
            raise
        
    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    def generate_advice(self, analysis: Dict[str, Any], dna: DecisionDNA) -> str:
        """Generate personalized advice"""
        try:
            if not analysis:
                raise ValueError("No analysis provided for advice generation")
            
            logger.info("Generating personalized advice")
            
            prompt = f"""Based on this analysis and Decision DNA, provide personalized advice:

Analysis: {json.dumps(analysis, indent=2)}
Decision DNA: {asdict(dna)}

Provide:
1. Clear recommendation with reasoning
2. Action steps for next 30/60/90 days
3. Warning signs to watch for
4. Success indicators
5. Contingency plans

Be direct, actionable, and personalized to their DNA. Format as clear, readable text."""
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise ValueError("Empty response from Gemini API")
            
            advice = response.text.strip()
            
            if len(advice) < 50:
                raise ValueError("Advice response too short, likely incomplete")
            
            logger.info("Personalized advice generated successfully")
            return advice
            
        except Exception as e:
            logger.error(f"Error in generate_advice: {e}")
            raise

class TrackerAgent:
    """Tracks decisions and learns from outcomes"""
    def __init__(self):
        self.decisions_log = []
        
    def log_decision(self, decision: str, chosen_path: str, reasoning: str):
        """Log a decision for future learning"""
        self.decisions_log.append({
            'timestamp': datetime.now().isoformat(),
            'decision': decision,
            'chosen_path': chosen_path,
            'reasoning': reasoning
        })
        
    def get_decision_history(self) -> List[Dict[str, Any]]:
        return self.decisions_log

class FutureYouOrchestrator:
    """Main orchestrator coordinating all agents"""
    def __init__(self):
        self.profiler = ProfilerAgent()
        self.simulator = SimulatorAgent()
        self.analyzer = AnalyzerAgent()
        self.advisor = AdvisorAgent()
        self.tracker = TrackerAgent()
        self.memory = MemoryBank()
        
    def create_session(self, user_data: Dict[str, Any]) -> Session:
        """Create new session with user profile"""
        session = Session(
            session_id=f"session_{int(time.time())}",
            user_profile=user_data,
            decision_dna=None,
            scenarios=[],
            conversation_history=[],
            created_at=datetime.now().isoformat()
        )
        return session
        
    def simulate_decision(self, session: Session, decision: str, timelines: List[str] = ['1yr', '3yr', '5yr'], generate_visuals: bool = False) -> Dict[str, Any]:
        """Main workflow: simulate a decision across multiple timelines"""
        print(f"\n🔮 FutureYou: Simulating your decision...")
        
        # Step 1: Extract Decision DNA if not exists
        if not session.decision_dna:
            print("📊 Profiler Agent: Analyzing your Decision DNA...")
            session.decision_dna = self.profiler.analyze_profile(session.user_profile)
            print(f"✅ Decision DNA extracted: Risk={session.decision_dna.risk_tolerance:.2f}, Values={session.decision_dna.value_priorities}")
        
        # Step 2: Simulate futures (parallel for each timeline)
        print(f"\n🌐 Simulator Agent: Generating scenarios for {len(timelines)} timelines...")
        all_scenarios = []
        for timeline in timelines:
            scenarios = self.simulator.simulate_futures(decision, session.decision_dna, timeline)
            all_scenarios.extend(scenarios)
            print(f"  ✓ {timeline}: {len(scenarios)} scenarios generated")
        
        session.scenarios = all_scenarios
        
        # Step 3: Analyze scenarios
        print("\n🔍 Analyzer Agent: Comparing scenarios...")
        analysis = self.analyzer.analyze_scenarios(all_scenarios, session.decision_dna)
        print(f"✅ Analysis complete: Best scenario identified")
        
        # Step 4: Generate advice
        print("\n💡 Advisor Agent: Crafting personalized recommendations...")
        advice = self.advisor.generate_advice(analysis, session.decision_dna)
        print("✅ Recommendations ready")
        
        # Step 5: Save to memory
        self.memory.save_session(session)
        
        result = {
            'decision_dna': asdict(session.decision_dna),
            'scenarios': [asdict(s) for s in all_scenarios],
            'analysis': analysis,
            'advice': advice,
            'session_id': session.session_id
        }
        
        # Step 6: Generate visualizations if requested
        if generate_visuals:
            try:
                from visualizer import FutureYouVisualizer
                print("\n🎨 Generating visualizations...")
                viz = FutureYouVisualizer()
                
                os.makedirs("results/visualizations", exist_ok=True)
                
                result['visuals'] = {
                    'dna': viz.generate_dna_visualization(result['decision_dna'], f"results/visualizations/dna_{session.session_id}.png"),
                    'timeline': viz.generate_timeline_visualization(all_scenarios[:3], f"results/visualizations/timeline_{session.session_id}.png"),
                    'tree': viz.generate_decision_tree(decision, all_scenarios[:3], f"results/visualizations/tree_{session.session_id}.png"),
                    'architecture': viz.generate_architecture_diagram(f"results/visualizations/architecture_{session.session_id}.png")
                }
                print("✅ Visualizations generated")
            except Exception as e:
                print(f"⚠️  Visualization failed: {e}")
                import traceback
                traceback.print_exc()
        
        return result
        
    def track_decision(self, decision: str, chosen_path: str, reasoning: str):
        """Track a decision made by user"""
        self.tracker.log_decision(decision, chosen_path, reasoning)

def main():
    """Run FutureYou system with input from futureyou_input.json"""
    try:
        print("=" * 80)
        print("🔮 FUTUREYOU: Personal Future Simulator")
        print("=" * 80)
        
        # Load input from JSON file
        input_file = 'futureyou_input.json'
        
        if not os.path.exists(input_file):
            print(f"❌ Error: {input_file} not found!")
            print("Please create futureyou_input.json with your profile and decision.")
            print("See futureyou_input.json.example for template.")
            return 1
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            logger.info(f"Successfully loaded input from {input_file}")
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing {input_file}: {e}")
            logger.error(f"JSON parsing error: {e}")
            return 1
        except Exception as e:
            print(f"❌ Error reading {input_file}: {e}")
            logger.error(f"File reading error: {e}")
            return 1
        
        # Validate and extract data from input
        try:
            user_data = input_data.get('user_profile', {})
            decision = input_data.get('decision', '')
            timelines = input_data.get('timelines', ['1yr', '3yr', '5yr'])
            generate_visuals = input_data.get('generate_visuals', False)
            
            # Validate inputs
            if not user_data:
                raise ValueError("user_profile is required in input JSON")
            if not decision:
                raise ValueError("decision is required in input JSON")
            
            # Validate using InputValidator
            user_data = InputValidator.validate_user_profile(user_data)
            decision = InputValidator.validate_decision(decision)
            timelines = InputValidator.validate_timelines(timelines)
            
        except ValueError as e:
            print(f"❌ Input validation error: {e}")
            logger.error(f"Input validation error: {e}")
            return 1
        
        print(f"👤 User: {user_data.get('user_id', 'Unknown')}")
        print(f"🤔 Decision: {decision[:80]}{'...' if len(decision) > 80 else ''}")
        print(f"⏰ Timelines: {', '.join(timelines)}")
        print(f"🎨 Generate Visuals: {'Yes' if generate_visuals else 'No'}")
        print("=" * 80)
    
        # Create output directories
        try:
            os.makedirs("results/outputs", exist_ok=True)
            os.makedirs("results/visualizations", exist_ok=True)
            logger.info("Output directories created")
        except Exception as e:
            print(f"❌ Error creating output directories: {e}")
            logger.error(f"Directory creation error: {e}")
            return 1
        
        # Create orchestrator and run simulation
        try:
            print("🚀 Initializing AI agents...")
            orchestrator = FutureYouOrchestrator()
            session = orchestrator.create_session(user_data)
            logger.info("Orchestrator and session created successfully")
            
            print("⚡ Starting simulation...")
            start_time = time.time()
            
            result = orchestrator.simulate_decision(
                session, 
                decision, 
                timelines=timelines, 
                generate_visuals=generate_visuals
            )
            
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Simulation completed in {duration:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error during simulation: {e}")
            logger.error(f"Simulation error: {e}")
            return 1
    
        # Display results
        try:
            print("\n" + "=" * 80)
            print("📊 SIMULATION RESULTS")
            print("=" * 80)
            
            print(f"\n🧬 Your Decision DNA:")
            dna = result['decision_dna']
            print(f"  • Risk Tolerance: {dna['risk_tolerance']:.2f} ({'Low' if dna['risk_tolerance'] < 0.3 else 'Medium' if dna['risk_tolerance'] < 0.7 else 'High'})")
            print(f"  • Time Preference: {dna['time_horizon_preference']}")
            print(f"  • Top Values: {', '.join(dna['value_priorities'][:3])}")
            
            print(f"\n🌐 Generated {len(result['scenarios'])} Future Scenarios")
            for i, scenario in enumerate(result['scenarios'][:3]):  # Show first 3
                print(f"\n  [{scenario['timeline']}] {scenario['decision_path']}")
                print(f"    📊 Probability: {scenario['probability']:.0%}")
                if scenario['outcomes']:
                    outcome_preview = list(scenario['outcomes'].values())[0]
                    print(f"    🎯 Key Outcome: {outcome_preview}")
            
            print(f"\n🔍 Analysis Insights:")
            analysis = result['analysis']
            print(f"  • 🏆 Best Scenario: {analysis.get('best_scenario', 'N/A')}")
            print(f"  • ⚖️  Key Trade-offs: {str(analysis.get('trade_offs', 'N/A'))[:100]}{'...' if len(str(analysis.get('trade_offs', ''))) > 100 else ''}")
            
            print(f"\n💡 Personalized Advice:")
            advice_preview = result['advice'][:400] + "..." if len(result['advice']) > 400 else result['advice']
            print(advice_preview)
            
            # Save results with HTML report
            print("\n📁 Saving results...")
            from result_visualizer import save_results
            
            # Update save_results to use new directory structure
            saved_files = save_results(result, user_data, decision, output_dir="results/outputs")
            
            print("\n" + "=" * 80)
            print(f"✅ Session completed: {result['session_id']}")
            print(f"⏱️  Duration: {duration:.1f} seconds")
            print(f"📄 HTML Report: {saved_files['html_report']}")
            print(f"📁 JSON Result: {saved_files['json_result']}")
            print(f"📋 Summary: {saved_files['json_summary']}")
            if 'visuals' in result:
                print(f"🎨 Visualizations: results/visualizations/")
            print(f"🌐 View all: results/outputs/index.html")
            print("=" * 80)
            
            return 0
            
        except Exception as e:
            print(f"❌ Error saving results: {e}")
            logger.error(f"Results saving error: {e}")
            return 1
            
    except KeyboardInterrupt:
        print("\n❌ Simulation interrupted by user")
        logger.info("Simulation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Unexpected error in main: {e}")
        return 1

if __name__ == "__main__":
    main()
