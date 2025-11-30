#!/usr/bin/env python3
"""
FutureYou Visualizer
Generates visual representations of timelines, decision trees, and architecture
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class FutureYouVisualizer:
    """Generate visual representations using Gemini image generation"""
    
    def __init__(self, image_model="gemini-2.5-flash-image-preview"):
        self.model = genai.GenerativeModel(image_model)
    
    def generate_timeline_visualization(self, scenarios, output_path="timeline_visualization.png"):
        """Generate visual timeline showing 1yr/3yr/5yr scenarios"""
        
        # Create prompt for timeline visualization
        prompt = f"""Create a professional, clean timeline infographic showing three future scenarios:

1 YEAR: {scenarios[0].decision_path[:100]}
Probability: {scenarios[0].probability:.0%}

3 YEAR: {scenarios[1].decision_path[:100] if len(scenarios) > 1 else 'N/A'}
Probability: {scenarios[1].probability:.0%} if len(scenarios) > 1 else 'N/A'

5 YEAR: {scenarios[2].decision_path[:100] if len(scenarios) > 2 else 'N/A'}
Probability: {scenarios[2].probability:.0%} if len(scenarios) > 2 else 'N/A'

Style: Modern, minimalist, professional business infographic with timeline arrows, clean typography, blue and green color scheme"""
        
        response = self.model.generate_content(prompt)
        
        # Save generated image
        if hasattr(response, '_result') and response._result.candidates:
            for part in response._result.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data.data:
                    image_data = part.inline_data.data
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    return output_path
        
        # If no image, create a text file with the response
        with open(output_path.replace('.png', '.txt'), 'w') as f:
            f.write(f"Generated content:\n{response.text if hasattr(response, 'text') else str(response)}")
        return output_path.replace('.png', '.txt')
    
    def generate_decision_tree(self, decision, scenarios, output_path="decision_tree.png"):
        """Generate decision tree visualization"""
        
        prompt = f"""Create a clean decision tree diagram showing:

ROOT DECISION: {decision[:150]}

Branch 1 (Optimistic): {scenarios[0].decision_path[:80]}
→ Outcome: {list(scenarios[0].outcomes.values())[0][:60] if scenarios[0].outcomes else 'Success'}
→ Probability: {scenarios[0].probability:.0%}

Branch 2 (Realistic): {scenarios[1].decision_path[:80] if len(scenarios) > 1 else 'N/A'}
→ Outcome: {list(scenarios[1].outcomes.values())[0][:60] if len(scenarios) > 1 and scenarios[1].outcomes else 'Moderate'}
→ Probability: {scenarios[1].probability:.0%} if len(scenarios) > 1 else 'N/A'

Branch 3 (Pessimistic): {scenarios[2].decision_path[:80] if len(scenarios) > 2 else 'N/A'}
→ Outcome: {list(scenarios[2].outcomes.values())[0][:60] if len(scenarios) > 2 and scenarios[2].outcomes else 'Challenge'}
→ Probability: {scenarios[2].probability:.0%} if len(scenarios) > 2 else 'N/A'

Style: Professional flowchart, clean lines, modern design, blue/green/red color coding for optimistic/realistic/pessimistic"""
        
        response = self.model.generate_content(prompt)
        
        if hasattr(response, '_result') and response._result.candidates:
            for part in response._result.candidates[0].content.parts:
                if hasattr(part, 'inline_data'):
                    image_data = part.inline_data.data
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    return output_path
        
        raise Exception("No image generated")
    
    def generate_architecture_diagram(self, output_path="architecture_diagram.png"):
        """Generate system architecture visualization"""
        
        prompt = """Create a professional system architecture diagram showing:

TOP: FutureYou Orchestrator (central coordinator)

LAYER 1: Five AI Agents in sequence:
- Profiler Agent (extracts Decision DNA)
- Simulator Agent (generates scenarios - parallel execution)
- Analyzer Agent (compares outcomes)
- Advisor Agent (provides recommendations)
- Tracker Agent (learns from decisions - loop)

BOTTOM: Memory Bank (long-term storage)

Show data flow with arrows between components. Use modern tech diagram style with clean boxes, professional colors (blue, purple, green), and clear labels. Include "Gemini 3 Pro" badges on AI agents."""
        
        response = self.model.generate_content(prompt)
        
        if hasattr(response, '_result') and response._result.candidates:
            for part in response._result.candidates[0].content.parts:
                if hasattr(part, 'inline_data'):
                    image_data = part.inline_data.data
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    return output_path
        
        raise Exception("No image generated")
    
    def generate_dna_visualization(self, dna, output_path="decision_dna.png"):
        """Generate Decision DNA visualization"""
        
        prompt = f"""Create an infographic showing personal Decision DNA profile:

RISK TOLERANCE: {dna['risk_tolerance']:.0%} (show as gauge/meter)
TIME PREFERENCE: {dna['time_horizon_preference'].upper()}
TOP VALUES: {', '.join(dna['value_priorities'][:3])}
EMOTIONAL DRIVERS: {', '.join(dna['emotional_drivers'][:2])}

Style: Modern data visualization, clean design, use icons and charts, professional color scheme (blue/purple gradient)"""
        
        response = self.model.generate_content(prompt)
        
        if hasattr(response, '_result') and response._result.candidates:
            for part in response._result.candidates[0].content.parts:
                if hasattr(part, 'inline_data'):
                    image_data = part.inline_data.data
                    with open(output_path, 'wb') as f:
                        f.write(image_data)
                    return output_path
        
        raise Exception("No image generated")

def main():
    """Demo visualizer"""
    print("🎨 FutureYou Visualizer Demo")
    print("Using: gemini-3-pro-image-preview")
    print("=" * 60)
    
    visualizer = FutureYouVisualizer()
    
    # Sample data
    sample_scenarios = [
        {
            'decision_path': 'Join AI startup as founding engineer',
            'probability': 0.7,
            'outcomes': {'career': 'Rapid growth and equity gains'}
        },
        {
            'decision_path': 'Stay at FAANG with promotion track',
            'probability': 0.6,
            'outcomes': {'career': 'Steady progression and stability'}
        },
        {
            'decision_path': 'Startup fails, return to job market',
            'probability': 0.2,
            'outcomes': {'career': 'Career setback but lessons learned'}
        }
    ]
    
    sample_dna = {
        'risk_tolerance': 0.65,
        'time_horizon_preference': 'medium',
        'value_priorities': ['wealth', 'impact', 'freedom'],
        'emotional_drivers': ['achievement', 'autonomy']
    }
    
    try:
        print("\n📊 Generating architecture diagram...")
        arch_path = visualizer.generate_architecture_diagram()
        print(f"✅ Saved: {arch_path}")
        
        print("\n🧬 Generating Decision DNA visualization...")
        dna_path = visualizer.generate_dna_visualization(sample_dna)
        print(f"✅ Saved: {dna_path}")
        
        print("\n🌐 Generating timeline visualization...")
        timeline_path = visualizer.generate_timeline_visualization(sample_scenarios)
        print(f"✅ Saved: {timeline_path}")
        
        print("\n🌳 Generating decision tree...")
        tree_path = visualizer.generate_decision_tree(
            "Should I join an AI startup or stay at FAANG?",
            sample_scenarios
        )
        print(f"✅ Saved: {tree_path}")
        
        print("\n" + "=" * 60)
        print("✅ All visualizations generated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Note: gemini-3-pro-image-preview may not be available yet")

if __name__ == "__main__":
    main()
