#!/usr/bin/env python3
"""
Result Visualizer for FutureYou
Creates HTML reports and organized file outputs
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

def format_advice_html(advice_text):
    """Format advice text for better HTML display"""
    lines = advice_text.split('\n')
    formatted_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        if not line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            continue
            
        # Headers
        if line.startswith('###'):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h4 style="color: #2c3e50; margin-top: 20px; margin-bottom: 10px;">{line.replace("###", "").strip()}</h4>')
        elif line.startswith('##'):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h3 style="color: #2c3e50; margin-top: 25px; margin-bottom: 15px;">{line.replace("##", "").strip()}</h3>')
        elif line.startswith('#'):
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<h3 style="color: #2c3e50; margin-top: 25px; margin-bottom: 15px;">{line.replace("#", "").strip()}</h3>')
        # Numbered items
        elif len(line) > 0 and line[0].isdigit() and '. ' in line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<div style="margin: 15px 0; padding: 15px; background: #e8f4fd; border-left: 4px solid #007bff; border-radius: 5px;"><strong>{line}</strong></div>')
        # Bullet points
        elif line.startswith('*') or line.startswith('-'):
            if not in_list:
                formatted_lines.append('<ul style="margin: 10px 0; padding-left: 20px;">')
                in_list = True
            # Handle bold text in bullet points
            content = line[1:].strip()
            if '**' in content:
                content = content.replace('**', '<strong>').replace('**', '</strong>')
            formatted_lines.append(f'<li style="margin: 8px 0; line-height: 1.6;">{content}</li>')
        # Bold text
        elif '**' in line:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            # Handle multiple bold sections
            import re
            line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            formatted_lines.append(f'<p style="margin: 12px 0; line-height: 1.6;">{line}</p>')
        # Separator lines
        elif line.strip() == '--' or line.strip() == '---':
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append('<hr style="margin: 20px 0; border: none; border-top: 2px solid #eee;">')
        else:
            if in_list:
                formatted_lines.append('</ul>')
                in_list = False
            formatted_lines.append(f'<p style="margin: 12px 0; line-height: 1.6;">{line}</p>')
    
    # Close any open list
    if in_list:
        formatted_lines.append('</ul>')
    
    return '\n'.join(formatted_lines)

def create_html_report(result, user_profile, decision, output_dir):
    """Create beautiful HTML report of results"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FutureYou Results - {user_profile['user_id']}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; }}
        .section {{ padding: 25px; border-bottom: 1px solid #eee; }}
        .dna-card {{ background: #f8f9ff; border-left: 4px solid #667eea; padding: 20px; margin: 15px 0; border-radius: 5px; }}
        .scenario {{ background: #fff; border: 1px solid #e1e5e9; border-radius: 8px; padding: 20px; margin: 15px 0; }}
        .scenario-header {{ font-weight: bold; color: #2c3e50; margin-bottom: 10px; }}
        .probability {{ background: #27ae60; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.9em; }}
        .risk {{ color: #e74c3c; }}
        .opportunity {{ color: #27ae60; }}
        .advice {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 8px; margin: 15px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #667eea; }}
        .metric-label {{ font-size: 0.9em; color: #666; }}
        h1, h2, h3 {{ margin-top: 0; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔮 FutureYou Simulation Results</h1>
            <p><strong>User:</strong> {user_profile['user_id']} | <strong>Age:</strong> {user_profile['age']} | <strong>Role:</strong> {user_profile['current_role']}</p>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="section">
            <h2>🤔 Decision Scenario</h2>
            <p style="font-size: 1.1em; line-height: 1.6; background: #f8f9fa; padding: 15px; border-radius: 5px;">
                "{decision}"
            </p>
        </div>

        <div class="section">
            <h2>🧬 Your Decision DNA</h2>
            <div class="dna-card">
                <div class="metric">
                    <div class="metric-value">{result['decision_dna']['risk_tolerance']:.2f}</div>
                    <div class="metric-label">Risk Tolerance</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{result['decision_dna']['time_horizon_preference'].title()}</div>
                    <div class="metric-label">Time Preference</div>
                </div>
                <div style="margin-top: 15px;">
                    <strong>Top Values:</strong> {', '.join(result['decision_dna']['value_priorities'][:3])}
                </div>
                <div style="margin-top: 10px;">
                    <strong>Decision Patterns:</strong>
                    <ul>
"""
    
    patterns = result['decision_dna']['decision_patterns']
    if isinstance(patterns, str):
        html_content += f"<li>{patterns}</li>"
    else:
        for pattern in patterns:
            html_content += f"<li>{pattern}</li>"
    
    html_content += f"""
                    </ul>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🌐 Future Scenarios ({len(result['scenarios'])} Generated)</h2>
"""
    
    for i, scenario in enumerate(result['scenarios'], 1):
        html_content += f"""
            <div class="scenario">
                <div class="scenario-header">
                    Scenario {i} [{scenario['timeline']}] 
                    <span class="probability">{scenario['probability']:.0%} Probability</span>
                </div>
                <p><strong>Path:</strong> {scenario['decision_path']}</p>
                
                <h4>Key Outcomes:</h4>
                <ul>
"""
        for key, value in scenario['outcomes'].items():
            html_content += f"<li><strong>{key.title()}:</strong> {value}</li>"
        
        html_content += f"""
                </ul>
                
                <div style="display: flex; gap: 30px; margin-top: 15px;">
                    <div>
                        <h4 class="risk">⚠️ Risks:</h4>
                        <ul>
"""
        for risk in scenario['risks'][:3]:
            html_content += f"<li class='risk'>{risk}</li>"
        
        html_content += f"""
                        </ul>
                    </div>
                    <div>
                        <h4 class="opportunity">🚀 Opportunities:</h4>
                        <ul>
"""
        for opp in scenario['opportunities'][:3]:
            html_content += f"<li class='opportunity'>{opp}</li>"
        
        html_content += """
                        </ul>
                    </div>
                </div>
            </div>
"""
    
    html_content += f"""
        </div>

        <div class="section">
            <h2>🔍 Analysis Insights</h2>
            <div style="background: #e8f4fd; padding: 20px; border-radius: 8px;">
                <p><strong>Best Scenario:</strong> {result['analysis'].get('best_scenario', 'N/A')}</p>
                <p><strong>Risk Assessment:</strong> {result['analysis'].get('risk_analysis', {}).get('description', 'N/A')}</p>
            </div>
        </div>

        <div class="section">
            <h2>💡 Personalized Advice</h2>
            <div class="advice">
                {format_advice_html(result['advice'])}
            </div>
        </div>

        <div class="section">
            <h2>📊 Session Information</h2>
            <p><strong>Session ID:</strong> {result['session_id']}</p>
            <p><strong>Scenarios Generated:</strong> {len(result['scenarios'])}</p>
            <p><strong>Analysis Points:</strong> {len(result['analysis'])}</p>
            <p><strong>Advice Length:</strong> {len(result['advice'])} characters</p>
        </div>
    </div>
</body>
</html>
"""
    
    html_file = os.path.join(output_dir, f"futureyou_report_{user_profile['user_id']}_{int(time.time())}.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file

def save_structured_results(result, user_profile, decision, output_dir):
    """Save results in organized JSON structure"""
    
    timestamp = int(time.time())
    
    # Main result file
    result_file = os.path.join(output_dir, f"result_{user_profile['user_id']}_{timestamp}.json")
    
    structured_result = {
        "metadata": {
            "user_id": user_profile['user_id'],
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "decision": decision
        },
        "user_profile": user_profile,
        "decision_dna": result['decision_dna'],
        "scenarios": result['scenarios'],
        "analysis": result['analysis'],
        "advice": result['advice'],
        "session_id": result['session_id']
    }
    
    with open(result_file, 'w') as f:
        json.dump(structured_result, f, indent=2, default=str)
    
    # Summary file
    summary_file = os.path.join(output_dir, f"summary_{user_profile['user_id']}_{timestamp}.json")
    
    summary = {
        "user": user_profile['user_id'],
        "decision": decision[:100] + "..." if len(decision) > 100 else decision,
        "risk_tolerance": result['decision_dna']['risk_tolerance'],
        "top_values": result['decision_dna']['value_priorities'][:3],
        "scenarios_count": len(result['scenarios']),
        "best_scenario": result['analysis'].get('best_scenario', 'N/A'),
        "timestamp": datetime.now().isoformat()
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    return result_file, summary_file



def create_results_index(output_dir):
    """Create index.html to list all results"""
    
    try:
        html_files = [f for f in os.listdir(output_dir) if f.endswith('.html') and f != 'index.html']
        json_files = [f for f in os.listdir(output_dir) if f.startswith('summary_') and f.endswith('.json')]
        
        index_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>FutureYou Results Index</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #f5f7fa; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .result-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
        h1 {{ color: #2c3e50; }}
        a {{ color: #667eea; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 FutureYou Results Index</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>📊 Simulation Results ({len(html_files)} reports)</h2>
"""
        
        for html_file in sorted(html_files, reverse=True):
            file_path = os.path.join(output_dir, html_file)
            if os.path.exists(file_path):
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                index_content += f"""
        <div class="result-item">
            <a href="{html_file}" target="_blank">{html_file}</a>
            <div class="timestamp">Generated: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
"""
        
        index_content += """
    </div>
</body>
</html>
"""
        
        with open(os.path.join(output_dir, "index.html"), 'w', encoding='utf-8') as f:
            f.write(index_content)
            
    except Exception as e:
        print(f"Warning: Could not create index file: {e}")

def save_results(result, user_profile, decision, output_dir="results/outputs"):
    """Main function to save all result formats"""
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        # Save HTML report
        html_file = create_html_report(result, user_profile, decision, output_dir)
        
        # Save structured JSON
        result_file, summary_file = save_structured_results(result, user_profile, decision, output_dir)
        
        # Update index
        create_results_index(output_dir)
        
        return {
            'html_report': html_file,
            'json_result': result_file,
            'json_summary': summary_file
        }
        
    except Exception as e:
        print(f"Error saving results: {e}")
        raise