"""
End-to-End Test Script for Agent Orchestration

This script tests the complete agent orchestration workflow
from frontend input to backend processing and response.
"""

import asyncio
import json
import time
from typing import Dict, Any, List
import httpx
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:9000"
TEST_TIMEOUT = 30  # seconds


class AgentOrchestrationTester:
    """Test suite for agent orchestration system"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TEST_TIMEOUT)
        self.test_results = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def test_health_check(self) -> bool:
        """Test basic API health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            result = response.status_code == 200
            self.test_results.append({
                "test": "health_check",
                "result": result,
                "status_code": response.status_code,
                "response": response.json() if result else None
            })
            return result
        except Exception as e:
            self.test_results.append({
                "test": "health_check",
                "result": False,
                "error": str(e)
            })
            return False
    
    async def test_orchestration_health(self) -> bool:
        """Test orchestration system health"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/orchestration/health")
            result = response.status_code == 200
            self.test_results.append({
                "test": "orchestration_health",
                "result": result,
                "status_code": response.status_code,
                "response": response.json() if result else None
            })
            return result
        except Exception as e:
            self.test_results.append({
                "test": "orchestration_health",
                "result": False,
                "error": str(e)
            })
            return False
    
    async def test_start_orchestration(self, inputs: List[Dict[str, Any]]) -> str:
        """Test starting orchestration workflow"""
        try:
            payload = {
                "inputs": inputs,
                "metadata": {
                    "test": True,
                    "timestamp": time.time()
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/orchestration/start",
                json=payload
            )
            
            result = response.status_code == 200
            response_data = response.json() if result else None
            
            self.test_results.append({
                "test": "start_orchestration",
                "result": result,
                "status_code": response.status_code,
                "response": response_data,
                "event_id": response_data.get("event_id") if result else None
            })
            
            return response_data.get("event_id") if result else None
            
        except Exception as e:
            self.test_results.append({
                "test": "start_orchestration",
                "result": False,
                "error": str(e)
            })
            return None
    
    async def test_workflow_status(self, event_id: str) -> Dict[str, Any]:
        """Test getting workflow status"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/orchestration/status/{event_id}"
            )
            
            result = response.status_code == 200
            response_data = response.json() if result else None
            
            self.test_results.append({
                "test": "workflow_status",
                "result": result,
                "status_code": response.status_code,
                "response": response_data,
                "event_id": event_id
            })
            
            return response_data if result else {}
            
        except Exception as e:
            self.test_results.append({
                "test": "workflow_status",
                "result": False,
                "error": str(e),
                "event_id": event_id
            })
            return {}
    
    async def test_memory_stats(self) -> bool:
        """Test memory store statistics"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/orchestration/stats")
            result = response.status_code == 200
            self.test_results.append({
                "test": "memory_stats",
                "result": result,
                "status_code": response.status_code,
                "response": response.json() if result else None
            })
            return result
        except Exception as e:
            self.test_results.append({
                "test": "memory_stats",
                "result": False,
                "error": str(e)
            })
            return False
    
    async def test_user_feedback(self, event_id: str, feedback: Dict[str, Any]) -> bool:
        """Test adding user feedback"""
        try:
            payload = {"feedback": feedback}
            response = await self.client.post(
                f"{self.base_url}/api/v1/orchestration/feedback/{event_id}",
                json=payload
            )
            
            result = response.status_code == 200
            self.test_results.append({
                "test": "user_feedback",
                "result": result,
                "status_code": response.status_code,
                "response": response.json() if result else None,
                "event_id": event_id
            })
            return result
            
        except Exception as e:
            self.test_results.append({
                "test": "user_feedback",
                "result": False,
                "error": str(e),
                "event_id": event_id
            })
            return False
    
    async def wait_for_completion(self, event_id: str, max_wait: int = 30) -> Dict[str, Any]:
        """Wait for workflow completion"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = await self.test_workflow_status(event_id)
            
            if status.get("workflow_status") in ["completed", "error"]:
                return status
            
            await asyncio.sleep(2)  # Poll every 2 seconds
        
        return {"workflow_status": "timeout", "error": "Workflow did not complete in time"}
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """Run complete end-to-end test"""
        print("🚀 Starting Agent Orchestration E2E Test")
        
        # Test 1: Health checks
        print("1. Testing health checks...")
        health_ok = await self.test_health_check()
        orchestration_health_ok = await self.test_orchestration_health()
        
        if not health_ok or not orchestration_health_ok:
            return {
                "success": False,
                "error": "Health checks failed",
                "results": self.test_results
            }
        
        # Test 2: Memory stats
        print("2. Testing memory stats...")
        await self.test_memory_stats()
        
        # Test 3: Start orchestration
        print("3. Starting orchestration...")
        test_inputs = [
            {
                "source_type": "text",
                "content": "jungle themed birthday party for 5 year old",
                "tags": ["jungle", "birthday", "kids", "theme"],
                "metadata": {
                    "test_input": True,
                    "age": 5,
                    "theme": "jungle"
                }
            }
        ]
        
        event_id = await self.test_start_orchestration(test_inputs)
        if not event_id:
            return {
                "success": False,
                "error": "Failed to start orchestration",
                "results": self.test_results
            }
        
        print(f"   Event ID: {event_id}")
        
        # Test 4: Monitor workflow
        print("4. Monitoring workflow progress...")
        final_status = await self.wait_for_completion(event_id)
        
        print(f"   Final status: {final_status.get('workflow_status')}")
        
        # Test 5: Add feedback
        print("5. Testing user feedback...")
        feedback = {
            "rating": 5,
            "comment": "Great test!",
            "test_feedback": True
        }
        await self.test_user_feedback(event_id, feedback)
        
        # Test 6: Final status check
        print("6. Final status check...")
        final_check = await self.test_workflow_status(event_id)
        
        # Compile results
        success = (
            health_ok and 
            orchestration_health_ok and 
            event_id and 
            final_status.get("workflow_status") == "completed"
        )
        
        return {
            "success": success,
            "event_id": event_id,
            "final_status": final_status,
            "final_check": final_check,
            "results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed_tests": len([r for r in self.test_results if r.get("result", False)]),
                "failed_tests": len([r for r in self.test_results if not r.get("result", False)])
            }
        }


async def run_test():
    """Run the complete test suite"""
    async with AgentOrchestrationTester() as tester:
        result = await tester.run_complete_test()
        
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        
        if result["success"]:
            print("✅ All tests PASSED!")
        else:
            print("❌ Some tests FAILED!")
        
        print(f"Event ID: {result.get('event_id', 'N/A')}")
        print(f"Final Status: {result.get('final_status', {}).get('workflow_status', 'N/A')}")
        
        summary = result.get("summary", {})
        print(f"Tests: {summary.get('passed_tests', 0)}/{summary.get('total_tests', 0)} passed")
        
        # Print detailed results
        print("\nDetailed Results:")
        for test_result in result.get("results", []):
            status = "✅" if test_result.get("result", False) else "❌"
            test_name = test_result.get("test", "unknown")
            print(f"  {status} {test_name}")
            
            if not test_result.get("result", False) and "error" in test_result:
                print(f"    Error: {test_result['error']}")
        
        # Save results to file
        results_file = Path("test_results.json")
        with open(results_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        return result


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(run_test())
    
    # Exit with appropriate code
    exit(0 if result["success"] else 1)
