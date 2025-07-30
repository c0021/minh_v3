#!/usr/bin/env python3
"""
Market Data Bridge Optimization Progress Checker
===============================================

Interactive script to check current progress, update tasks, and view detailed status.
Provides real-time insights into the optimization implementation.

Usage:
    python scripts/check_progress.py
    python scripts/check_progress.py --phase 2
    python scripts/check_progress.py --summary
"""

import json
import sys
import os
from datetime import datetime
from typing import Dict, Any
import argparse

class ProgressTracker:
    def __init__(self, tracker_file: str = "PROGRESS_TRACKER.json"):
        self.tracker_file = tracker_file
        self.data = self.load_tracker()
    
    def load_tracker(self) -> Dict[str, Any]:
        """Load progress tracker data"""
        try:
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Progress tracker file not found: {self.tracker_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing progress tracker: {e}")
            sys.exit(1)
    
    def save_tracker(self):
        """Save progress tracker data"""
        self.data['last_updated'] = datetime.now().isoformat() + 'Z'
        with open(self.tracker_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        print(f"✅ Progress tracker updated: {self.tracker_file}")
    
    def show_summary(self):
        """Display overall project summary"""
        print("🎯 MARKET DATA BRIDGE OPTIMIZATION - PROGRESS SUMMARY")
        print("=" * 60)
        
        # Overall progress
        progress = self.data['overall_progress']
        status = self.data['status']
        print(f"📊 Overall Progress: {progress}% - {status}")
        
        # Progress bar
        filled = int(progress / 5)  # 20 chars for 100%
        bar = "█" * filled + "░" * (20 - filled)
        print(f"    {bar} {progress}%")
        print()
        
        # Phase summary
        print("📋 PHASE SUMMARY:")
        for phase_id, phase in self.data['phases'].items():
            status_icon = "✅" if phase['status'] == 'completed' else "🚀" if phase['status'] == 'planning' else "⏳"
            print(f"  {status_icon} {phase['name']}: {phase['progress']}% ({phase['status']})")
        
        # Key metrics
        print("\n📈 KEY PERFORMANCE INDICATORS:")
        for kpi, details in self.data['key_performance_indicators'].items():
            status_icon = "✅" if details['status'] == 'achieved' else "🔄" if details['status'] == 'on_track' else "⏳"
            print(f"  {status_icon} {kpi.replace('_', ' ').title()}: {details['current']} → {details['target']}")
        
        # Next actions
        print(f"\n🎯 NEXT ACTIONS:")
        for action in self.data['next_actions']['immediate']:
            print(f"  • {action}")
        
        print(f"\n📅 Timeline: {self.data['timeline']['sessions_completed']}/{self.data['timeline']['sessions_required']} sessions")
        print(f"🎯 Target Completion: {self.data['timeline']['estimated_completion']}")
    
    def show_phase_detail(self, phase_num: int):
        """Show detailed information for a specific phase"""
        phase_id = f"phase_{phase_num}"
        
        if phase_id not in self.data['phases']:
            print(f"❌ Phase {phase_num} not found")
            return
        
        phase = self.data['phases'][phase_id]
        print(f"🎯 PHASE {phase_num}: {phase['name'].upper()}")
        print("=" * 50)
        
        # Phase overview
        status_icon = "✅" if phase['status'] == 'completed' else "🚀" if phase['status'] == 'planning' else "⏳"
        print(f"{status_icon} Status: {phase['status']} ({phase['progress']}%)")
        print(f"📅 Duration: {phase['duration_sessions']} sessions")
        
        if phase.get('start_date'):
            print(f"🚀 Started: {phase['start_date']}")
        if phase.get('completion_date'):
            print(f"✅ Completed: {phase['completion_date']}")
        
        # Success criteria
        criteria_met = phase['success_criteria_met']
        criteria_total = phase['success_criteria_total']
        criteria_pct = int((criteria_met / criteria_total) * 100) if criteria_total > 0 else 0
        print(f"🎯 Success Criteria: {criteria_met}/{criteria_total} ({criteria_pct}%)")
        
        # Tasks
        print(f"\n📋 TASKS:")
        for task_id, task in phase['tasks'].items():
            status_icon = "✅" if task['status'] == 'completed' else "🚀" if task['status'] == 'in_progress' else "⏳"
            task_name = task_id.replace('_', ' ').title()
            print(f"  {status_icon} {task_name}: {task['progress']}%")
            
            if task.get('notes'):
                print(f"      💡 {task['notes']}")
            
            if task.get('dependencies'):
                deps = ', '.join(task['dependencies'])
                print(f"      🔗 Dependencies: {deps}")
            
            if task.get('estimated_time'):
                print(f"      ⏱️  Estimated: {task['estimated_time']}")
        
        # Target metrics (if available)
        if 'target_metrics' in phase:
            print(f"\n📊 TARGET METRICS:")
            for metric, target in phase['target_metrics'].items():
                print(f"  • {metric.replace('_', ' ').title()}: {target}")
    
    def update_task_progress(self, phase_num: int, task_name: str, progress: int, status: str = None, notes: str = None):
        """Update progress for a specific task"""
        phase_id = f"phase_{phase_num}"
        
        if phase_id not in self.data['phases']:
            print(f"❌ Phase {phase_num} not found")
            return
        
        # Find task by name (flexible matching)
        task_key = None
        for key in self.data['phases'][phase_id]['tasks'].keys():
            if task_name.lower() in key.lower() or key.lower() in task_name.lower():
                task_key = key
                break
        
        if not task_key:
            print(f"❌ Task '{task_name}' not found in Phase {phase_num}")
            available_tasks = list(self.data['phases'][phase_id]['tasks'].keys())
            print(f"Available tasks: {', '.join(available_tasks)}")
            return
        
        # Update task
        task = self.data['phases'][phase_id]['tasks'][task_key]
        task['progress'] = progress
        
        if status:
            task['status'] = status
        
        if notes:
            task['notes'] = notes
        
        # Update phase progress (average of all tasks)
        phase_tasks = self.data['phases'][phase_id]['tasks']
        total_progress = sum(t['progress'] for t in phase_tasks.values())
        avg_progress = int(total_progress / len(phase_tasks))
        self.data['phases'][phase_id]['progress'] = avg_progress
        
        # Update overall progress (weighted average of phases)
        phase_weights = {'phase_1': 0.2, 'phase_2': 0.3, 'phase_3': 0.25, 'phase_4': 0.15, 'phase_5': 0.1}
        overall_progress = sum(
            self.data['phases'][pid]['progress'] * weight 
            for pid, weight in phase_weights.items()
        )
        self.data['overall_progress'] = int(overall_progress)
        
        print(f"✅ Updated {task_key}: {progress}% ({status or task['status']})")
        print(f"📊 Phase {phase_num} progress: {avg_progress}%")
        print(f"🎯 Overall progress: {self.data['overall_progress']}%")
        
        self.save_tracker()
    
    def show_risks(self):
        """Display risk assessment"""
        print("⚠️  RISK ASSESSMENT")
        print("=" * 30)
        
        for risk_id, risk in self.data['risks'].items():
            risk_name = risk_id.replace('_', ' ').title()
            prob = risk['probability'].upper()
            impact = risk['impact'].upper()
            
            # Risk level color coding
            if prob == 'HIGH' and impact == 'HIGH':
                icon = "🔴"
            elif prob == 'MEDIUM' or impact == 'HIGH':
                icon = "🟡"
            else:
                icon = "🟢"
            
            print(f"{icon} {risk_name}")
            print(f"   📊 Probability: {prob} | Impact: {impact}")
            print(f"   🛡️  Mitigation: {risk['mitigation']}")
            print(f"   📋 Status: {risk['status']}")
            print()
    
    def show_next_session_plan(self):
        """Show what should be done in the next session"""
        print("📅 NEXT SESSION PLAN")
        print("=" * 25)
        
        print("🎯 IMMEDIATE ACTIONS:")
        for action in self.data['next_actions']['immediate']:
            print(f"  • {action}")
        
        print(f"\n🚀 NEXT SESSION TASKS:")
        for action in self.data['next_actions']['next_session']:
            print(f"  • {action}")
        
        # Find current active phase
        current_phase = None
        for phase_id, phase in self.data['phases'].items():
            if phase['status'] in ['planning', 'in_progress']:
                current_phase = phase_id.split('_')[1]
                break
        
        if current_phase:
            print(f"\n🎯 Focus: Phase {current_phase} - {self.data['phases'][f'phase_{current_phase}']['name']}")

def main():
    parser = argparse.ArgumentParser(description='Market Data Bridge Optimization Progress Tracker')
    parser.add_argument('--phase', type=int, help='Show detailed view of specific phase (1-5)')
    parser.add_argument('--summary', action='store_true', help='Show project summary (default)')
    parser.add_argument('--risks', action='store_true', help='Show risk assessment')
    parser.add_argument('--next', action='store_true', help='Show next session plan')
    parser.add_argument('--update', nargs=4, metavar=('PHASE', 'TASK', 'PROGRESS', 'STATUS'), 
                       help='Update task progress: --update 2 "websocket" 50 "in_progress"')
    
    args = parser.parse_args()
    
    # Change to implementation directory to find tracker file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    impl_dir = os.path.dirname(script_dir)  # Go up from scripts/ to implementation/market_data_bridge_optimization/
    os.chdir(impl_dir)
    
    tracker = ProgressTracker()
    
    if args.update:
        phase, task, progress, status = args.update
        tracker.update_task_progress(int(phase), task, int(progress), status)
    elif args.phase:
        tracker.show_phase_detail(args.phase)
    elif args.risks:
        tracker.show_risks()
    elif args.next:
        tracker.show_next_session_plan()
    else:
        tracker.show_summary()

if __name__ == "__main__":
    main()