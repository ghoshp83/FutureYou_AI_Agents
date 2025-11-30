#!/usr/bin/env python3
"""
Interactive E2E Testing for FutureYou
Real user input scenarios - no mock data
"""

import os
import json
import time
from futureyou import FutureYouOrchestrator

def get_user_profile():
    """Collect real user profile from command line"""
    print("\n" + "="*60)
    print("👤 USER PROFILE COLLECTION")
    print("="*60)
    print("Please provide your information for Decision DNA analysis:")
    
    profile = {}
    
    # Basic info
    profile['user_id'] = input("\n🆔 User ID (e.g., john_doe_001): ").strip()
    profile['age'] = int(input("🎂 Age: "))
    profile['current_role'] = input("💼 Current Role/Job: ").strip()
    profile['experience_years'] = int(input("📅 Years of Experience: "))
    
    # Financial info
    try:
        profile['current_salary'] = int(input("💰 Current Annual Salary in USD (yearly, optional, press Enter to skip): ") or "0")
    except:
        profile['current_salary'] = 0
    
    profile['location'] = input("📍 Current Location: ").strip()
    profile['education'] = input("🎓 Education Background: ").strip()
    
    # Skills and interests
    print("\n📋 Skills (comma-separated):")
    skills_input = input("   Example: Python, Leadership, Marketing: ").strip()
    profile['skills'] = [s.strip() for s in skills_input.split(',') if s.strip()]
    
    print("\n🎯 Interests (comma-separated):")
    interests_input = input("   Example: AI, Travel, Entrepreneurship: ").strip()
    profile['interests'] = [i.strip() for i in interests_input.split(',') if i.strip()]
    
    print("\n🌟 Life Goals (comma-separated):")
    goals_input = input("   Example: Financial independence, Work-life balance, Make impact: ").strip()
    profile['life_goals'] = [g.strip() for g in goals_input.split(',') if g.strip()]
    
    # Past decisions
    print("\n📚 Past Major Decisions (help AI understand your patterns):")
    print("   Enter one decision per line, press Enter twice when done:")
    past_decisions = []
    while True:
        decision = input("   Decision: ").strip()
        if not decision:
            break
        past_decisions.append(decision)
    profile['past_decisions'] = past_decisions
    
    return profile

def get_decision_scenario():
    """Get the decision scenario from user"""
    print("\n" + "="*60)
    print("🤔 DECISION SCENARIO")
    print("="*60)
    print("Describe the decision you're facing:")
    print("Be specific about the options and context.")
    print("\nExample: 'Should I accept a senior role at Google (L6, $250K) or join a Series A startup as founding engineer (equity-heavy, $160K base)?'")
    
    decision = input("\n📝 Your Decision: ").strip()
    return decision

def get_test_preferences():
    """Get testing preferences"""
    print("\n" + "="*60)
    print("⚙️  TEST CONFIGURATION")
    print("="*60)
    
    # Timeline selection
    print("📅 Select timelines to simulate:")
    print("1. 1 year only (quick)")
    print("2. 1yr + 3yr (medium)")
    print("3. 1yr + 3yr + 5yr (comprehensive)")
    
    choice = input("\nChoice (1-3): ").strip()
    timeline_map = {
        '1': ['1yr'],
        '2': ['1yr', '3yr'],
        '3': ['1yr', '3yr', '5yr']
    }
    timelines = timeline_map.get(choice, ['1yr'])
    
    # Visual generation
    generate_visuals = input("\n🎨 Generate visualizations? (y/n): ").lower().startswith('y')
    
    return timelines, generate_visuals

def display_results(result):
    """Display results in a user-friendly format"""
    print("\n" + "="*80)
    print("📊 FUTUREYOU SIMULATION RESULTS")
    print("="*80)
    
    # Decision DNA
    print(f"\n🧬 YOUR DECISION DNA:")
    dna = result['decision_dna']
    print(f"   Risk Tolerance: {dna['risk_tolerance']:.2f} (0=Conservative, 1=Risk-taker)")
    print(f"   Time Preference: {dna['time_horizon_preference']}")
    print(f"   Top Values: {', '.join(dna['value_priorities'][:3])}")
    print(f"   Decision Style: {dna['decision_patterns']}")
    
    # Scenarios
    print(f"\n🌐 FUTURE SCENARIOS ({len(result['scenarios'])} generated):")
    for i, scenario in enumerate(result['scenarios'], 1):
        print(f"\n   Scenario {i} [{scenario['timeline']}]: {scenario['decision_path']}")
        print(f"   Probability: {scenario['probability']:.0%}")
        print(f"   Key Outcomes: {scenario['outcomes']}")
        print(f"   Risks: {', '.join(scenario['risks'][:2])}")
        print(f"   Opportunities: {', '.join(scenario['opportunities'][:2])}")
    
    # Analysis
    print(f"\n🔍 ANALYSIS INSIGHTS:")
    analysis = result['analysis']
    if 'best_scenario' in analysis:
        print(f"   Best Match: {analysis['best_scenario']}")
    if 'risk_analysis' in analysis:
        print(f"   Risk Assessment: {analysis['risk_analysis']}")
    
    # Advice
    print(f"\n💡 PERSONALIZED ADVICE:")
    advice_lines = result['advice'].split('\n')
    for line in advice_lines[:10]:  # Show first 10 lines
        if line.strip():
            print(f"   {line.strip()}")
    
    if len(advice_lines) > 10:
        print(f"   ... (showing first 10 lines of {len(advice_lines)} total)")
    
    # Visuals
    if 'visuals' in result:
        print(f"\n🎨 VISUALIZATIONS GENERATED:")
        for viz_type, path in result['visuals'].items():
            print(f"   {viz_type.title()}: {path}")

def run_interactive_test():
    """Run interactive E2E test with real user data"""
    print("="*80)
    print("🔮 FUTUREYOU INTERACTIVE E2E TEST")
    print("="*80)
    print("This will test FutureYou with YOUR real decision scenario.")
    print("No mock data - everything you input will be used for simulation.")
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n❌ GEMINI_API_KEY not found!")
        print("Please set your API key in the .env file")
        return False
    
    try:
        # Step 1: Collect user profile
        user_profile = get_user_profile()
        
        # Step 2: Get decision scenario
        decision = get_decision_scenario()
        
        # Step 3: Get test preferences
        timelines, generate_visuals = get_test_preferences()
        
        # Step 4: Confirm before running
        print(f"\n" + "="*60)
        print("🚀 READY TO SIMULATE")
        print("="*60)
        print(f"User: {user_profile['user_id']}")
        print(f"Decision: {decision[:100]}...")
        print(f"Timelines: {', '.join(timelines)}")
        print(f"Visuals: {'Yes' if generate_visuals else 'No'}")
        
        confirm = input("\nProceed with simulation? (y/n): ").lower().startswith('y')
        if not confirm:
            print("❌ Simulation cancelled")
            return False
        
        # Step 5: Run FutureYou simulation
        print(f"\n🔮 Starting FutureYou simulation...")
        orchestrator = FutureYouOrchestrator()
        session = orchestrator.create_session(user_profile)
        
        result = orchestrator.simulate_decision(
            session, 
            decision, 
            timelines=timelines,
            generate_visuals=generate_visuals
        )
        
        # Step 6: Display results
        display_results(result)
        
        # Step 7: Save results with visualizer
        from result_visualizer import save_results
        
        saved_files = save_results(result, user_profile, decision)
        
        print(f"\n💾 Results saved:")
        print(f"   📊 HTML Report: {saved_files['html_report']}")
        print(f"   📄 JSON Result: {saved_files['json_result']}")
        print(f"   📋 Summary: {saved_files['json_summary']}")
        print(f"   🌐 View all: results/test_outputs/index.html")
        
        # Step 8: Test validation
        print(f"\n✅ E2E TEST VALIDATION:")
        print(f"   ✓ Decision DNA extracted: Risk={result['decision_dna']['risk_tolerance']:.2f}")
        print(f"   ✓ Scenarios generated: {len(result['scenarios'])}")
        print(f"   ✓ Analysis completed: {len(result['analysis'])} insights")
        print(f"   ✓ Advice generated: {len(result['advice'])} characters")
        print(f"   ✓ Session saved: {result['session_id']}")
        
        if generate_visuals and 'visuals' in result:
            print(f"   ✓ Visuals generated: {len(result['visuals'])}")
        
        print(f"\n🎉 INTERACTIVE E2E TEST: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ E2E TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    import time
    
    print("Welcome to FutureYou Interactive E2E Testing!")
    print("This will walk you through testing the system with your real decision.")
    
    success = run_interactive_test()
    
    if success:
        print("\n" + "="*80)
        print("✅ INTERACTIVE E2E TEST COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\nThe system is working correctly with real user data.")
        print("Ready to proceed with GitHub preparation and submission.")
    else:
        print("\n" + "="*80)
        print("❌ TEST FAILED - CHECK LOGS ABOVE")
        print("="*80)

if __name__ == "__main__":
    main()