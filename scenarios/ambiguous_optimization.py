#!/usr/bin/env python3
"""
Ambiguous Scenario: Performance & Reliability Optimization
==========================================================

Scenario: Business stakeholders say "Make the URL shortener faster 
and more reliable." This is ambiguous. We need to:
1. Interpret the intent
2. Ask clarifying questions
3. Define measurable metrics
4. Identify bottlenecks
5. Propose specific improvements
6. Validate improvements with evidence

This demonstrates:
- Requirement clarification
- Stakeholder communication
- Trade-off analysis
- Performance testing
- Cost-benefit analysis
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmbiguousScenario:
    """Handles ambiguous requirements with clarification and decomposition."""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.ambiguity_resolution = {}
        self.results = {}
        
    def run(self) -> Dict[str, Any]:
        """Execute the ambiguous scenario."""
        print("=" * 60)
        print("AMBIGUOUS SCENARIO: 'Make it Faster and More Reliable'")
        print("=" * 60)
        print("\n❓ AMBIGUOUS REQUIREMENT:")
        print('   "Make the URL shortener faster and more reliable"')
        print("   - No specific metrics")
        print("   - No definition of 'faster' or 'more reliable'")
        print("   - No scope defined")
        print("   - No budget or timeline\n")
        
        # Step 1: Clarify the requirement
        print("🔍 STEP 1: Requirement Clarification")
        clarified = self._clarify_requirement()
        print(f"\n   📋 CLARIFIED REQUIREMENTS:")
        print(f"   - Speed target: {clarified['speed_target']}")
        print(f"   - Reliability target: {clarified['reliability_target']}")
        print(f"   - Scope: {clarified['scope']}")
        print(f"   - Budget: {clarified['budget']}")
        print(f"   - Timeline: {clarified['timeline']}")
        print(f"   - Success criteria: {', '.join(clarified['success_criteria'])}")
        self.results['clarified'] = clarified
        
        # Step 2: Identify bottlenecks
        print("\n🔬 STEP 2: Bottleneck Identification")
        bottlenecks = self._identify_bottlenecks()
        print("\n   🎯 BOTTLENECKS IDENTIFIED:")
        for i, b in enumerate(bottlenecks, 1):
            print(f"   {i}. {b['component']}: {b['issue']} (Impact: {b['impact']})")
            print(f"      - Current: {b['current']}")
            print(f"      - Target: {b['target']}")
        self.results['bottlenecks'] = bottlenecks
        
        # Step 3: Generate solutions
        print("\n💡 STEP 3: Solution Proposals")
        solutions = self._generate_solutions(bottlenecks, clarified)
        print("\n   🛠️  PROPOSED SOLUTIONS:")
        for solution in solutions:
            print(f"\n   📌 {solution['name']}")
            print(f"      - Description: {solution['description']}")
            print(f"      - Expected improvement: {solution['improvement']}")
            print(f"      - Effort: {solution['effort']}")
            print(f"      - Cost: {solution['cost']}")
            print(f"      - Risk: {solution['risk']}")
        self.results['solutions'] = solutions
        
        # Step 4: Trade-off analysis
        print("\n⚖️  STEP 4: Trade-off Analysis")
        tradeoffs = self._analyze_tradeoffs(solutions, clarified)
        print("\n   📊 TRADE-OFF MATRIX:")
        print(f"   {'Solution':<30} {'Performance':<15} {'Cost':<15} {'Complexity':<15} {'Time':<15}")
        print("   " + "-" * 90)
        for t in tradeoffs:
            print(f"   {t['name']:<30} {t['performance']:<15} {t['cost']:<15} {t['complexity']:<15} {t['time']:<15}")
        self.results['tradeoffs'] = tradeoffs
        
        # Step 5: Recommendations
        print("\n🎯 STEP 5: Recommendations")
        recommendations = self._make_recommendations(solutions, tradeoffs, clarified)
        print(f"\n   ✅ RECOMMENDED APPROACH:")
        print(f"   - Primary: {recommendations['primary']['name']}")
        print(f"     Rationale: {recommendations['primary']['rationale']}")
        print(f"   - Secondary: {recommendations['secondary']['name']}")
        print(f"     Rationale: {recommendations['secondary']['rationale']}")
        print(f"   - Timeline: {recommendations['timeline']}")
        self.results['recommendations'] = recommendations
        
        # Step 6: Implementation plan
        print("\n📅 STEP 6: Implementation Plan")
        plan = self._create_implementation_plan(recommendations)
        print("\n   📋 PHASED APPROACH:")
        for phase in plan:
            print(f"\n   Phase {phase['phase']}: {phase['name']}")
            print(f"   - Duration: {phase['duration']}")
            print(f"   - Deliverables: {', '.join(phase['deliverables'])}")
            print(f"   - Success metrics: {', '.join(phase['metrics'])}")
        self.results['plan'] = plan
        
        # Step 7: Risk mitigation
        print("\n🛡️  STEP 7: Risk Mitigation")
        risks = self._identify_risks(plan)
        print("\n   ⚠️  RISKS & MITIGATIONS:")
        for risk in risks:
            print(f"\n   - {risk['risk']}")
            print(f"     Likelihood: {risk['likelihood']}")
            print(f"     Impact: {risk['impact']}")
            print(f"     Mitigation: {risk['mitigation']}")
        self.results['risks'] = risks
        
        # Step 8: Validation plan
        print("\n✅ STEP 8: Validation Plan")
        validation = self._validation_plan()
        print("\n   🔬 VALIDATION METHODOLOGY:")
        print(f"   - Load testing: {validation['load_testing']}")
        print(f"   - Performance benchmarking: {validation['benchmarking']}")
        print(f"   - Reliability testing: {validation['reliability_testing']}")
        print(f"   - Success criteria: {', '.join(validation['success_criteria'])}")
        self.results['validation'] = validation
        
        print("\n📊 Ambiguous Summary:")
        print(f"   - Clarified ambiguous requirement into {len(clarified['success_criteria'])} measurable criteria")
        print(f"   - Identified {len(bottlenecks)} bottlenecks")
        print(f"   - Generated {len(solutions)} potential solutions")
        print(f"   - Recommended phased implementation over {recommendations['timeline']}")
        
        return self.results
    
    def _clarify_requirement(self) -> Dict:
        """Clarify ambiguous requirements."""
        return {
            "clarifying_questions": [
                "What is the current p95 latency?",
                "What is the current uptime?",
                "What is the peak traffic volume?",
                "What is the acceptable budget increase?",
                "What is the timeline for improvements?"
            ],
            "assumptions": {
                "speed": "Latency < 100ms p95",
                "reliability": "Uptime > 99.9%"
            },
            "speed_target": "100ms p95 latency",
            "reliability_target": "99.99% uptime",
            "scope": "All endpoints, focusing on redirect (read) path",
            "budget": "$500/month additional",
            "timeline": "2 weeks",
            "success_criteria": [
                "P95 latency < 100ms (currently 150ms)",
                "Uptime > 99.99% (currently 99.9%)",
                "Error rate < 0.01% (currently 0.05%)",
                "CPU usage < 70% at peak"
            ]
        }
    
    def _identify_bottlenecks(self) -> List[Dict]:
        """Identify performance and reliability bottlenecks."""
        return [
            {
                "component": "Database",
                "issue": "Slow queries on redirect (no index on short_code)",
                "impact": "high",
                "current": "25ms average query time",
                "target": "< 5ms"
            },
            {
                "component": "Cache",
                "issue": "Low cache hit rate (40%)",
                "impact": "high",
                "current": "40% cache hit rate",
                "target": "> 90%"
            },
            {
                "component": "Network",
                "issue": "Single region deployment causes latency for global users",
                "impact": "medium",
                "current": "150ms average latency",
                "target": "< 50ms"
            },
            {
                "component": "Application",
                "issue": "Synchronous blocking operations",
                "impact": "medium",
                "current": "Requests blocked on DB queries",
                "target": "Async operations"
            },
            {
                "component": "Monitoring",
                "issue": "No proactive alerting",
                "impact": "medium",
                "current": "Reactive monitoring only",
                "target": "Proactive alerts"
            }
        ]
    
    def _generate_solutions(self, bottlenecks: List[Dict], clarified: Dict) -> List[Dict]:
        """Generate solutions for each bottleneck."""
        return [
            {
                "name": "Add Database Indexes",
                "description": "Create indexes on short_code and created_at",
                "improvement": "50% reduction in query time",
                "effort": "Low (2 hours)",
                "cost": "$0",
                "risk": "Low",
                "addresses": ["Database"]
            },
            {
                "name": "Improve Cache Strategy",
                "description": "Increase TTL and pre-warm cache",
                "improvement": "60% cache hit rate increase",
                "effort": "Medium (2 days)",
                "cost": "$0",
                "risk": "Low",
                "addresses": ["Cache"]
            },
            {
                "name": "Global CDN Deployment",
                "description": "Deploy to multiple regions using CloudFront",
                "improvement": "70% reduction in global latency",
                "effort": "High (5 days)",
                "cost": "$300/month",
                "risk": "Medium",
                "addresses": ["Network"]
            },
            {
                "name": "Async Processing",
                "description": "Convert sync code to async/await",
                "improvement": "30% improvement in throughput",
                "effort": "High (3 days)",
                "cost": "$0",
                "risk": "Medium",
                "addresses": ["Application"]
            },
            {
                "name": "Proactive Monitoring",
                "description": "Set up Prometheus alerts and dashboards",
                "improvement": "Faster incident response",
                "effort": "Medium (2 days)",
                "cost": "$0",
                "risk": "Low",
                "addresses": ["Monitoring"]
            }
        ]
    
    def _analyze_tradeoffs(self, solutions: List[Dict], clarified: Dict) -> List[Dict]:
        """Analyze trade-offs between solutions."""
        return [
            {
                "name": "Add Database Indexes",
                "performance": 8,
                "cost": 10,
                "complexity": 10,
                "time": 10,
                "tradeoffs": ["Minimal downside"]
            },
            {
                "name": "Improve Cache Strategy",
                "performance": 7,
                "cost": 10,
                "complexity": 8,
                "time": 8,
                "tradeoffs": ["May use more memory"]
            },
            {
                "name": "Global CDN Deployment",
                "performance": 9,
                "cost": 5,
                "complexity": 6,
                "time": 6,
                "tradeoffs": ["Ongoing cost", "Complex setup"]
            },
            {
                "name": "Async Processing",
                "performance": 8,
                "cost": 10,
                "complexity": 5,
                "time": 7,
                "tradeoffs": ["Code complexity"]
            },
            {
                "name": "Proactive Monitoring",
                "performance": 6,
                "cost": 10,
                "complexity": 8,
                "time": 8,
                "tradeoffs": ["No direct performance benefit"]
            }
        ]
    
    def _make_recommendations(self, solutions: List[Dict], tradeoffs: List[Dict], 
                              clarified: Dict) -> Dict:
        """Make final recommendations."""
        return {
            "primary": {
                "name": "Add Database Indexes + Improve Cache Strategy",
                "rationale": "Maximum impact with minimum effort and cost"
            },
            "secondary": {
                "name": "Async Processing",
                "rationale": "Good long-term improvement"
            },
            "timeline": "2-3 weeks"
        }
    
    def _create_implementation_plan(self, recommendations: Dict) -> List[Dict]:
        """Create phased implementation plan."""
        return [
            {
                "phase": 1,
                "name": "Quick Wins",
                "duration": "3 days",
                "deliverables": [
                    "Database indexes",
                    "Cache TTL optimization",
                    "Basic monitoring"
                ],
                "metrics": [
                    "Query time < 10ms",
                    "Cache hit rate > 60%"
                ]
            },
            {
                "phase": 2,
                "name": "Async Migration",
                "duration": "4 days",
                "deliverables": [
                    "Async FastAPI routes",
                    "Connection pooling",
                    "Background tasks"
                ],
                "metrics": [
                    "Throughput increase 30%",
                    "CPU usage decrease 20%"
                ]
            },
            {
                "phase": 3,
                "name": "Global Optimization",
                "duration": "5 days",
                "deliverables": [
                    "CDN configuration",
                    "Multi-region deployment",
                    "Full monitoring stack"
                ],
                "metrics": [
                    "Global latency < 100ms",
                    "Uptime > 99.99%"
                ]
            }
        ]
    
    def _identify_risks(self, plan: List[Dict]) -> List[Dict]:
        """Identify and mitigate risks."""
        return [
            {
                "risk": "Database migration may cause downtime",
                "likelihood": "Medium",
                "impact": "High",
                "mitigation": "Use rolling migrations during low traffic"
            },
            {
                "risk": "Async code may introduce bugs",
                "likelihood": "Medium",
                "impact": "Medium",
                "mitigation": "Comprehensive testing and canary deployment"
            },
            {
                "risk": "CDN configuration complexity",
                "likelihood": "Low",
                "impact": "Medium",
                "mitigation": "Start with simple CloudFront setup"
            },
            {
                "risk": "Cost overruns",
                "likelihood": "Medium",
                "impact": "Medium",
                "mitigation": "Monitor costs daily, set budgets"
            }
        ]
    
    def _validation_plan(self) -> Dict:
        """Create validation plan."""
        return {
            "load_testing": "1000 req/s for 1 hour, measure p95 latency",
            "benchmarking": "Compare before/after with same load",
            "reliability_testing": "Chaos testing: kill cache, DB failover",
            "success_criteria": [
                "P95 latency < 100ms (was 150ms)",
                "Uptime > 99.99% (was 99.9%)",
                "Error rate < 0.01% (was 0.05%)",
                "CPU usage < 70% at peak",
                "Cache hit rate > 80% (was 40%)"
            ]
        }

def main():
    """Run ambiguous scenario."""
    scenario = AmbiguousScenario()
    result = scenario.run()
    
    # Save results
    output_dir = Path("./scenario_outputs/ambiguous")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to {output_dir}/result.json")

if __name__ == "__main__":
    main()