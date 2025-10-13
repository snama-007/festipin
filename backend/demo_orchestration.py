#!/usr/bin/env python3
"""
Agent Orchestration Demo Script

This script demonstrates the complete agent orchestration system
with real examples and interactive features.
"""

import asyncio
import json
import time
from typing import Dict, Any, List
from datetime import datetime

from app.services.simple_orchestrator import get_orchestrator
from app.services.local_memory_store import get_memory_store
from app.services.agent_registry import get_agent_registry


class AgentOrchestrationDemo:
    """Interactive demo of the agent orchestration system"""
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.memory_store = get_memory_store()
        self.agent_registry = get_agent_registry()
        
    async def run_demo(self):
        """Run the complete demo"""
        print("🎉 Welcome to Agent Orchestration Demo!")
        print("=" * 50)
        
        # Show system status
        await self.show_system_status()
        
        # Demo examples
        examples = [
            {
                "name": "Jungle Birthday Party",
                "inputs": [
                    {
                        "source_type": "text",
                        "content": "jungle themed birthday party for 5 year old with dinosaur cake",
                        "tags": ["jungle", "birthday", "kids", "dinosaur", "cake"],
                        "metadata": {"age": 5, "theme": "jungle"}
                    }
                ]
            },
            {
                "name": "Princess Tea Party",
                "inputs": [
                    {
                        "source_type": "text",
                        "content": "princess themed tea party for 7 year old girl",
                        "tags": ["princess", "tea", "party", "girls"],
                        "metadata": {"age": 7, "theme": "princess"}
                    }
                ]
            },
            {
                "name": "Space Adventure Party",
                "inputs": [
                    {
                        "source_type": "text",
                        "content": "space themed party with rocket decorations and astronaut costumes",
                        "tags": ["space", "rocket", "astronaut", "adventure"],
                        "metadata": {"theme": "space", "age_group": "kids"}
                    }
                ]
            }
        ]
        
        # Run each example
        for i, example in enumerate(examples, 1):
            print(f"\n🎯 Demo {i}: {example['name']}")
            print("-" * 30)
            await self.run_example(example)
            
            if i < len(examples):
                input("\nPress Enter to continue to next demo...")
        
        # Show final statistics
        await self.show_final_stats()
        
        print("\n🎊 Demo completed! Thank you for trying Agent Orchestration!")
    
    async def show_system_status(self):
        """Show current system status"""
        print("\n📊 System Status:")
        
        # Memory stats
        stats = await self.memory_store.get_memory_stats()
        print(f"  📁 Memory Store: {stats['active_events']} active events")
        print(f"  💾 Storage: {stats['total_size_mb']} MB")
        
        # Available agents
        agents = self.agent_registry.get_available_agents()
        print(f"  🤖 Agents: {len(agents)} available")
        for agent in agents:
            print(f"    - {agent.value}")
        
        print(f"  ⚡ Status: Ready for orchestration")
    
    async def run_example(self, example: Dict[str, Any]):
        """Run a single example"""
        print(f"Starting orchestration for: {example['name']}")
        
        # Start orchestration
        start_time = time.time()
        event_id = await self.orchestrator.start_orchestration(
            example['inputs'],
            {"demo": True, "example_name": example['name']}
        )
        
        print(f"✅ Event started: {event_id}")
        
        # Monitor progress
        await self.monitor_progress(event_id)
        
        # Show results
        await self.show_results(event_id)
        
        execution_time = time.time() - start_time
        print(f"⏱️  Total execution time: {execution_time:.2f} seconds")
    
    async def monitor_progress(self, event_id: str):
        """Monitor orchestration progress"""
        print("\n🔄 Monitoring agent progress...")
        
        completed_agents = set()
        max_wait = 30  # 30 seconds timeout
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = await self.orchestrator.get_workflow_status(event_id)
            
            if not status:
                print("❌ Failed to get status")
                return
            
            # Check for new completed agents
            current_agents = set(status['agent_results'].keys())
            new_agents = current_agents - completed_agents
            
            for agent_name in new_agents:
                agent_result = status['agent_results'][agent_name]
                if agent_result['status'] == 'completed':
                    print(f"  ✅ {agent_name}: Completed")
                    completed_agents.add(agent_name)
                elif agent_result['status'] == 'error':
                    print(f"  ❌ {agent_name}: Error - {agent_result.get('error', 'Unknown')}")
                    completed_agents.add(agent_name)
            
            # Check if workflow is complete
            if status['workflow_status'] in ['completed', 'error']:
                break
            
            await asyncio.sleep(1)  # Check every second
        
        if time.time() - start_time >= max_wait:
            print("⏰ Timeout reached")
    
    async def show_results(self, event_id: str):
        """Show orchestration results"""
        status = await self.orchestrator.get_workflow_status(event_id)
        
        if not status:
            print("❌ No results available")
            return
        
        print(f"\n📋 Results for Event: {event_id}")
        print("=" * 40)
        
        # Show agent results
        print("\n🤖 Agent Results:")
        for agent_name, result in status['agent_results'].items():
            print(f"\n  {agent_name}:")
            print(f"    Status: {result['status']}")
            if result['execution_time']:
                print(f"    Time: {result['execution_time']:.2f}s")
            
            # Show key results
            if result['status'] == 'completed' and result['result']:
                self._show_agent_result(agent_name, result['result'])
        
        # Show final plan
        if status.get('final_plan'):
            print(f"\n🎊 Final Plan:")
            final_plan = status['final_plan']
            
            if final_plan.get('event_summary'):
                summary = final_plan['event_summary']
                print(f"  Theme: {summary.get('theme', 'N/A')}")
                budget = summary.get('total_budget', {})
                if budget:
                    print(f"  Budget: ${budget.get('min', 0)} - ${budget.get('max', 0)}")
            
            if final_plan.get('recommendations'):
                print(f"\n  💡 Recommendations:")
                for rec in final_plan['recommendations']:
                    print(f"    • {rec}")
            
            if final_plan.get('next_steps'):
                print(f"\n  📝 Next Steps:")
                for i, step in enumerate(final_plan['next_steps'], 1):
                    print(f"    {i}. {step}")
    
    def _show_agent_result(self, agent_name: str, result: Dict[str, Any]):
        """Show specific agent result"""
        if agent_name == 'theme_agent':
            theme = result.get('primary_theme', 'N/A')
            confidence = result.get('confidence', 0)
            print(f"    Theme: {theme} (confidence: {confidence:.2f})")
            
        elif agent_name == 'cake_agent':
            cake_type = result.get('cake_type', 'N/A')
            flavor = result.get('flavor', 'N/A')
            print(f"    Type: {cake_type}, Flavor: {flavor}")
            
        elif agent_name == 'budget_agent':
            budget = result.get('total_budget', {})
            if budget:
                print(f"    Budget: ${budget.get('min', 0)} - ${budget.get('max', 0)}")
    
    async def show_final_stats(self):
        """Show final statistics"""
        print(f"\n📈 Final Statistics:")
        
        stats = await self.memory_store.get_memory_stats()
        print(f"  📁 Total Events: {stats['active_events']}")
        print(f"  💾 Storage Used: {stats['total_size_mb']} MB")
        
        # List recent events
        events = await self.memory_store.list_active_events()
        if events:
            print(f"\n📋 Recent Events:")
            for event_id in events[-3:]:  # Show last 3 events
                summary = await self.memory_store.get_event_summary(event_id)
                if summary:
                    print(f"  • {event_id}: {summary['workflow_status']}")


async def main():
    """Main demo function"""
    demo = AgentOrchestrationDemo()
    await demo.run_demo()


if __name__ == "__main__":
    print("🚀 Starting Agent Orchestration Demo...")
    asyncio.run(main())
