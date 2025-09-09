import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel
import pandas as pd

class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: str
    agent_name: str
    scenario: str
    action: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    adaptations_applied: Dict[str, Any] = {}
    performance_metrics: Dict[str, Any] = {}
    success: bool = True

class DynamicAuditLogger:
    def __init__(self):
        self.logs: List[AuditLogEntry] = []
    
    def log_dynamic_execution(
        self,
        agent_name: str,
        scenario: str,
        action: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        adaptations: Dict[str, Any] = None,
        performance: Dict[str, Any] = None,
        success: bool = True
    ) -> str:
        """Log dynamic agent execution"""
        log_id = str(uuid.uuid4())
        
        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=datetime.now().isoformat(),
            agent_name=agent_name,
            scenario=scenario,
            action=action,
            input_data=input_data,
            output_data=output_data,
            adaptations_applied=adaptations or {},
            performance_metrics=performance or {},
            success=success
        )
        
        self.logs.append(entry)
        return log_id
    
    def get_scenario_analytics(self, scenario: str) -> Dict[str, Any]:
        """Get analytics for specific scenario"""
        scenario_logs = [log for log in self.logs if log.scenario == scenario]
        
        if not scenario_logs:
            return {}
        
        return {
            "total_executions": len(scenario_logs),
            "success_rate": sum(1 for log in scenario_logs if log.success) / len(scenario_logs),
            "avg_processing_time": sum(
                log.performance_metrics.get("processing_time", 0) 
                for log in scenario_logs
            ) / len(scenario_logs),
            "most_used_adaptations": self._get_common_adaptations(scenario_logs),
            "agent_performance": self._get_agent_performance(scenario_logs)
        }
    
    def _get_common_adaptations(self, logs: List[AuditLogEntry]) -> Dict[str, int]:
        """Get most commonly used adaptations"""
        adaptations = {}
        for log in logs:
            for key, value in log.adaptations_applied.items():
                adaptations[f"{key}:{value}"] = adaptations.get(f"{key}:{value}", 0) + 1
        return dict(sorted(adaptations.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _get_agent_performance(self, logs: List[AuditLogEntry]) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by agent"""
        agent_perf = {}
        for log in logs:
            agent = log.agent_name
            if agent not in agent_perf:
                agent_perf[agent] = {"executions": 0, "successes": 0, "total_time": 0}
            
            agent_perf[agent]["executions"] += 1
            if log.success:
                agent_perf[agent]["successes"] += 1
            agent_perf[agent]["total_time"] += log.performance_metrics.get("processing_time", 0)
        
        # Calculate averages
        for agent, stats in agent_perf.items():
            stats["success_rate"] = stats["successes"] / stats["executions"] if stats["executions"] > 0 else 0
            stats["avg_time"] = stats["total_time"] / stats["executions"] if stats["executions"] > 0 else 0
        
        return agent_perf
    
    def export_scenario_report(self, scenario: str) -> str:
        """Export detailed scenario report"""
        analytics = self.get_scenario_analytics(scenario)
        scenario_logs = [log for log in self.logs if log.scenario == scenario]
        
        report = {
            "scenario": scenario,
            "report_generated": datetime.now().isoformat(),
            "analytics": analytics,
            "detailed_logs": [log.dict() for log in scenario_logs[-10:]]  # Last 10 executions
        }
        
        return json.dumps(report, indent=2)
