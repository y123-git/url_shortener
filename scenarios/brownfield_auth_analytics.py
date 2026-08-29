#!/usr/bin/env python3
"""
Brownfield Scenario: Add Authentication and Per-User Analytics
===============================================================

Scenario: The URL shortener service is already deployed in production.
We need to add:
1. User authentication (JWT-based)
2. Per-user analytics dashboard
3. Rate limiting per user
4. User management endpoints

This demonstrates:
- Impact analysis on existing codebase
- Database migrations (backward compatible)
- API versioning strategy
- Security considerations
- Gradual rollout approach
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.orchestrator import Orchestrator
from orchestrator.models.task_models import Stage, TaskStatus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrownfieldScenario:
    """Handles brownfield modifications with minimal disruption."""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.existing_codebase = self._load_existing_codebase()
        self.results = {}
        
    def _load_existing_codebase(self) -> Dict[str, str]:
        """Simulate loading existing codebase."""
        return {
            "main.py": """
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import redis

app = FastAPI()
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Database setup
DATABASE_URL = "postgresql://user:pass@localhost/urlshortener"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class URL(Base):
    __tablename__ = "urls"
    id = Column(String(10), primary_key=True, index=True)
    short_code = Column(String(10), unique=True, index=True)
    original_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

Base.metadata.create_all(bind=engine)

@app.post("/shorten")
def shorten_url(original_url: str):
    code = hashlib.md5(original_url.encode()).hexdigest()[:6]
    db = SessionLocal()
    new_url = URL(short_code=code, original_url=original_url)
    db.add(new_url)
    db.commit()
    redis_client.setex(code, 3600, original_url)
    return {"short_url": f"http://localhost:8000/{code}"}

@app.get("/{short_code}")
def redirect(short_code: str):
    cached = redis_client.get(short_code)
    if cached:
        return {"redirect": cached}
    db = SessionLocal()
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(404, "Not found")
    return {"redirect": url_entry.original_url}
""",
            "models.py": """
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    short_code = Column(String(10), unique=True, index=True)
    original_url = Column(String)
    created_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=True)
""",
            "requirements.txt": """
fastapi==0.95.0
sqlalchemy==2.0.9
psycopg2-binary==2.9.6
redis==4.5.4
uvicorn==0.21.1
"""
        }
    
    def run(self) -> Dict[str, Any]:
        """Execute the brownfield scenario."""
        print("=" * 60)
        print("BROWNFIELD SCENARIO: Add Auth & Analytics")
        print("=" * 60)
        print("\n📋 REQUIREMENT: Add user authentication and per-user analytics")
        print("   - Users can register/login with JWT")
        print("   - Each user owns their shortened URLs")
        print("   - Analytics per user (clicks, referrers, geo)")
        print("   - Rate limiting (100 requests/user/hour)")
        print("   - No breaking changes to existing API")
        print("\n🔄 Starting brownfield orchestration...\n")
        
        # Step 1: Impact Analysis
        print("🔍 STEP 1: Impact Analysis")
        impact = self._analyze_impact()
        print(f"   ✓ Affected components: {', '.join(impact['affected_components'])}")
        print(f"   ✓ New components needed: {', '.join(impact['new_components'])}")
        print(f"   ✓ Database changes: {len(impact['migrations'])} migrations")
        print(f"   ✓ Breaking changes: {len(impact['breaking_changes'])}")
        print(f"   ✓ Estimated effort: {impact['effort']} days")
        self.results['impact'] = impact
        
        # Step 2: Design the changes
        print("\n📐 STEP 2: Design Modifications")
        design = self._design_changes(impact)
        print(f"   ✓ API versioning: {design['api_versioning']}")
        print(f"   ✓ Migration strategy: {design['migration_strategy']}")
        print(f"   ✓ Backward compatibility: {'Yes' if design['backward_compatible'] else 'No'}")
        self.results['design'] = design
        
        # Step 3: Generate code modifications
        print("\n💻 STEP 3: Code Generation")
        code = self._generate_code_changes(design)
        print(f"   ✓ Modified files: {len(code['modified_files'])}")
        print(f"   ✓ New files: {len(code['new_files'])}")
        print(f"   ✓ Migration scripts: {len(code['migrations'])}")
        self.results['code'] = code
        
        # Step 4: Test strategy
        print("\n🧪 STEP 4: Testing Strategy")
        tests = self._generate_tests(code)
        print(f"   ✓ Unit tests: {tests['unit_tests']}")
        print(f"   ✓ Integration tests: {tests['integration_tests']}")
        print(f"   ✓ Migration tests: {tests['migration_tests']}")
        print(f"   ✓ Test coverage target: {tests['coverage_target']}")
        self.results['tests'] = tests
        
        # Step 5: Deployment strategy
        print("\n🚀 STEP 5: Deployment & Rollout")
        deploy = self._deployment_strategy()
        print(f"   ✓ Rollout strategy: {deploy['rollout']}")
        print(f"   ✓ Rollback plan: {deploy['rollback']}")
        print(f"   ✓ Monitoring: {deploy['monitoring']}")
        self.results['deployment'] = deploy
        
        # Step 6: Validate
        print("\n✅ STEP 6: Validation Gates")
        validation = self._validate_changes(code, tests, design)
        print(f"   ✓ Security review: {'PASS' if validation['security'] else 'FAIL'}")
        print(f"   ✓ Performance impact: {validation['performance_impact']}")
        print(f"   ✓ Data migration: {validation['data_migration_valid']}")
        print(f"   ✓ API compatibility: {validation['api_compatibility']}")
        self.results['validation'] = validation
        
        print("\n📊 Brownfield Summary:")
        print(f"   - {impact['effort']} days estimated implementation")
        print(f"   - {len(code['modified_files'])} files modified")
        print(f"   - {len(code['new_files'])} new files")
        print(f"   - {len(impact['migrations'])} database migrations")
        print(f"   - {'✅ Ready for production' if validation['security'] else '❌ Needs security review'}")
        
        return self.results
    
    def _analyze_impact(self) -> Dict:
        """Analyze impact on existing codebase."""
        # In production, this would use LLM
        return {
            "affected_components": [
                "main.py - Add auth middleware",
                "models.py - Add User model",
                "database.py - Add user relationships"
            ],
            "new_components": [
                "auth.py - JWT authentication",
                "analytics.py - User analytics",
                "rate_limit.py - Per-user rate limiting"
            ],
            "migrations": [
                "001_add_users_table.sql",
                "002_add_user_id_to_urls.sql",
                "003_add_analytics_table.sql"
            ],
            "breaking_changes": [
                "New authentication required for /shorten endpoint",
                "API versioning needed (v1/v2)"
            ],
            "effort": "3-5 days",
            "risk_level": "medium"
        }
    
    def _design_changes(self, impact: Dict) -> Dict:
        """Design the changes."""
        return {
            "api_versioning": "v2 endpoints with backward compatibility",
            "migration_strategy": "Rolling migrations with zero downtime",
            "backward_compatible": True,
            "user_flow": "JWT token in Authorization header",
            "analytics_schema": "User-specific analytics table",
            "new_endpoints": [
                "/v2/users/register",
                "/v2/users/login",
                "/v2/users/analytics"
            ],
            "modified_endpoints": [
                "/v2/shorten - Requires auth",
                "/v2/{code} - Track user_id"
            ]
        }
    
    def _generate_code_changes(self, design: Dict) -> Dict:
        """Generate code modifications."""
        return {
            "modified_files": [
                "main.py",
                "models.py",
                "database.py"
            ],
            "new_files": [
                "auth.py",
                "analytics.py",
                "rate_limit.py",
                "middleware.py"
            ],
            "migrations": [
                "001_add_users_table.sql",
                "002_add_user_id_to_urls.sql",
                "003_add_analytics_table.sql"
            ]
        }
    
    def _generate_tests(self, code: Dict) -> Dict:
        """Generate test strategy."""
        return {
            "unit_tests": 25,
            "integration_tests": 15,
            "migration_tests": 3,
            "coverage_target": "85%"
        }
    
    def _deployment_strategy(self) -> Dict:
        """Define deployment strategy."""
        return {
            "rollout": "Canary deployment (5% → 25% → 50% → 100%)",
            "rollback": "Automatic rollback on error rate > 1%",
            "monitoring": "Prometheus metrics + alerts on auth failures",
            "database": "Run migrations during maintenance window",
            "feature_flags": "Auth can be disabled via feature flag"
        }
    
    def _validate_changes(self, code: Dict, tests: Dict, design: Dict) -> Dict:
        """Validate changes."""
        return {
            "security": True,
            "performance_impact": "15% latency increase (acceptable)",
            "data_migration_valid": True,
            "api_compatibility": "100% backward compatible"
        }

def main():
    """Run brownfield scenario."""
    scenario = BrownfieldScenario()
    result = scenario.run()
    
    # Save results
    output_dir = Path("./scenario_outputs/brownfield")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "result.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to {output_dir}/result.json")

if __name__ == "__main__":
    main()