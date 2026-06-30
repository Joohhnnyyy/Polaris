from typing import List, Optional
import time
from backend.repositories.policy import PolicyRepository
from backend.repositories.root_cause import RootCauseRepository
from backend.models.models import Policy, RootCause

class PolicyService:
    def __init__(self, policy_repo: PolicyRepository, root_cause_repo: RootCauseRepository):
        self.policy_repo = policy_repo
        self.root_cause_repo = root_cause_repo
        # Cache policies
        self._cache_policies = []
        self._cache_root_causes = []
        self._cache_time_policy = 0.0
        self._cache_time_cause = 0.0
        self._ttl_seconds = 24 * 3600 # 24 Hours TTL

    def _refresh_cache(self):
        now = time.time()
        if not self._cache_policies or (now - self._cache_time_policy) > self._ttl_seconds:
            self._cache_policies = self.policy_repo.find_all()
            self._cache_time_policy = now
            
        if not self._cache_root_causes or (now - self._cache_time_cause) > self._ttl_seconds:
            self._cache_root_causes = self.root_cause_repo.find_all()
            self._cache_time_cause = now

    def get_policies_for_category(self, category: str) -> List[Policy]:
        self._refresh_cache()
        return [p for p in self._cache_policies if p.category == category]

    def get_root_causes_for_category(self, category: str) -> List[RootCause]:
        self._refresh_cache()
        return [rc for rc in self._cache_root_causes if rc.category == category]

    def evaluate_policy(self, category: str, risk_level: str, confidence: float, reports_count: int, votes_count: int) -> Optional[Policy]:
        policies = self.get_policies_for_category(category)
        if not policies:
            # Fallback to default policy
            self._refresh_cache()
            return self._cache_policies[0] if self._cache_policies else None

        for policy in policies:
            # Check conditions
            if confidence >= policy.minimum_confidence and reports_count >= policy.minimum_reports and votes_count >= policy.minimum_votes:
                # Check dispatch_if risk match if defined
                dispatch_risk = policy.dispatch_if.get("risk")
                if dispatch_risk and dispatch_risk != risk_level:
                    continue
                return policy

        return policies[0] if policies else None
