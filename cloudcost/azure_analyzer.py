"""
Azure Cost Analyzer - Detects wasteful spending patterns in Azure
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import os

try:
    from azure.identity import DefaultAzureCredential, AzureCliCredential
    from azure.mgmt.costmanagement import CostManagementClient
    from azure.mgmt.resource import ResourceManagementClient
    from azure.mgmt.subscription import SubscriptionClient
except ImportError:
    print("Azure SDK not installed. Run: pip install -r requirements.txt")
    raise


@dataclass
class WasteItem:
    """Represents a single wasteful resource"""
    resource_name: str
    resource_type: str
    waste_type: str
    current_cost: float
    potential_savings: float
    recommendation: str
    details: Dict


class AzureAnalyzer:
    """Analyzes Azure subscription for cost optimization opportunities"""
    
    def __init__(self, subscription_id: Optional[str] = None):
        """
        Initialize Azure analyzer
        
        Args:
            subscription_id: Azure subscription ID (will use default if not provided)
        """
        # Try AzureCLI credential first (most common for dev)
        try:
            self.credential = AzureCliCredential()
        except:
            self.credential = DefaultAzureCredential()
        
        # Get subscription ID
        if not subscription_id:
            subscription_id = self._get_default_subscription()
        
        self.subscription_id = subscription_id
        
        # Initialize clients
        self.cost_client = CostManagementClient(self.credential)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
    
    def _get_default_subscription(self) -> str:
        """Get default subscription ID from Azure CLI"""
        subscription_client = SubscriptionClient(self.credential)
        subscriptions = list(subscription_client.subscriptions.list())
        
        if not subscriptions:
            raise ValueError("No Azure subscriptions found. Run 'az login' first.")
        
        # Use first subscription
        return subscriptions[0].subscription_id
    
    def analyze(self) -> List[WasteItem]:
        """
        Run full cost analysis on Azure subscription
        
        Returns:
            List of WasteItem objects representing optimization opportunities
        """
        waste_items = []
        
        print("🔍 Analyzing Azure resources for waste...")
        
        # Get all resources
        resources = list(self.resource_client.resources.list())
        
        print(f"📊 Found {len(resources)} resources to analyze")
        
        # Check each resource type
        for resource in resources:
            # Analyze VMs
            if 'Microsoft.Compute/virtualMachines' in resource.type:
                vm_waste = self._analyze_vm(resource)
                if vm_waste:
                    waste_items.extend(vm_waste)
            
            # Analyze Storage
            elif 'Microsoft.Storage/storageAccounts' in resource.type:
                storage_waste = self._analyze_storage(resource)
                if storage_waste:
                    waste_items.extend(storage_waste)
            
            # Analyze Disks
            elif 'Microsoft.Compute/disks' in resource.type:
                disk_waste = self._analyze_disk(resource)
                if disk_waste:
                    waste_items.extend(disk_waste)
            
            # Analyze Public IPs
            elif 'Microsoft.Network/publicIPAddresses' in resource.type:
                ip_waste = self._analyze_public_ip(resource)
                if ip_waste:
                    waste_items.extend(ip_waste)
        
        print(f"✅ Analysis complete. Found {len(waste_items)} optimization opportunities")
        
        return waste_items
    
    def _analyze_vm(self, resource) -> List[WasteItem]:
        """Analyze VM for waste (oversized, idle, etc.)"""
        waste_items = []
        
        # Extract VM size from resource
        vm_name = resource.name
        
        # Simulated analysis (in real version, we'd check metrics)
        # For MVP, we'll use heuristics based on naming and tags
        
        # Check if it's a dev VM running 24/7
        if 'dev' in vm_name.lower() or 'test' in vm_name.lower():
            waste_items.append(WasteItem(
                resource_name=vm_name,
                resource_type='Virtual Machine',
                waste_type='dev_prod_mix',
                current_cost=150.0,  # Estimated
                potential_savings=100.0,  # 70% savings by scheduling
                recommendation="Schedule this dev VM to run only during work hours (9-5, Mon-Fri)",
                details={
                    'title': f'Dev VM "{vm_name}" Running 24/7',
                    'purpose': 'development work',
                    'size': 'Standard_D2s_v3',
                    'recommendation': 'Use Azure DevTest Labs or scheduled start/stop'
                }
            ))
        
        return waste_items
    
    def _analyze_storage(self, resource) -> List[WasteItem]:
        """Analyze storage accounts for waste"""
        waste_items = []
        
        storage_name = resource.name
        
        # Check for old storage (simulated)
        if 'backup' in storage_name.lower() or 'old' in storage_name.lower():
            waste_items.append(WasteItem(
                resource_name=storage_name,
                resource_type='Storage Account',
                waste_type='old_storage',
                current_cost=250.0,
                potential_savings=200.0,
                recommendation="Move to Archive tier or delete if not needed",
                details={
                    'title': f'Storage Account "{storage_name}" - Potential Archive Candidate',
                    'days': 547,
                    'recommendation': 'Review and move to Archive tier (90% cheaper)'
                }
            ))
        
        return waste_items
    
    def _analyze_disk(self, resource) -> List[WasteItem]:
        """Analyze disks for unattached resources"""
        waste_items = []
        
        disk_name = resource.name
        
        # In real version, check if disk is attached
        # For MVP, simulate finding unattached disks
        if 'unattached' in disk_name.lower() or 'old' in disk_name.lower():
            waste_items.append(WasteItem(
                resource_name=disk_name,
                resource_type='Managed Disk',
                waste_type='unattached_disk',
                current_cost=50.0,
                potential_savings=50.0,
                recommendation="Delete this disk or attach it to a VM",
                details={
                    'title': f'Unattached Disk "{disk_name}"',
                    'recommendation': 'This disk is not attached to any VM. Delete it.'
                }
            ))
        
        return waste_items
    
    def _analyze_public_ip(self, resource) -> List[WasteItem]:
        """Analyze public IPs for unused allocations"""
        waste_items = []
        
        # Simulated check for unused IPs
        # In real version, check if IP is associated
        
        return waste_items
    
    def get_total_monthly_cost(self) -> float:
        """
        Get total monthly cost (simplified for MVP)
        In production, this would query Cost Management API
        """
        # For MVP, return simulated total
        return 4237.89
    
    def estimate_savings(self, waste_items: List[WasteItem]) -> float:
        """Calculate total potential savings"""
        return sum(item.potential_savings for item in waste_items)


# Mock analyzer for testing without Azure credentials
class MockAzureAnalyzer:
    """Mock analyzer for testing and demo purposes"""
    
    def __init__(self, subscription_id: Optional[str] = None):
        self.subscription_id = subscription_id or "mock-subscription-123"
    
    def analyze(self) -> List[WasteItem]:
        """Return mock waste items for demo"""
        return [
            WasteItem(
                resource_name="VM-LargeIdiot-01",
                resource_type="Virtual Machine",
                waste_type="oversized_vm",
                current_cost=1200.0,
                potential_savings=1140.0,
                recommendation="Downsize to B2s ($60/mo) - you don't need 32 cores for a blog",
                details={
                    'title': 'VM-LargeIdiot-01 - Galactic Overkill',
                    'purpose': 'a WordPress site with 3 visitors',
                    'size': 'Standard_D32s_v3',
                    'recommendation': 'Downsize to B2s and save $1,140/month'
                }
            ),
            WasteItem(
                resource_name="storage-backup-backup-old",
                resource_type="Storage Account",
                waste_type="old_storage",
                current_cost=850.0,
                potential_savings=720.0,
                recommendation="Move to Archive tier - this data is colder than your ex's heart",
                details={
                    'title': 'Storage Account "backup-backup-backup-old"',
                    'days': 847,
                    'recommendation': 'Move to Archive tier, save $720/mo'
                }
            ),
            WasteItem(
                resource_name="dev-vm-test-something",
                resource_type="Virtual Machine",
                waste_type="dev_prod_mix",
                current_cost=180.0,
                potential_savings=120.0,
                recommendation="Schedule to run only during work hours (Mon-Fri, 9-5)",
                details={
                    'title': 'Dev VM running 24/7 like it has insomnia',
                    'purpose': 'testing',
                    'size': 'Standard_D2s_v3',
                    'recommendation': 'Use scheduled start/stop'
                }
            ),
            WasteItem(
                resource_name="disk-unattached-1",
                resource_type="Managed Disk",
                waste_type="unattached_disk",
                current_cost=75.0,
                potential_savings=75.0,
                recommendation="Delete this orphaned disk immediately",
                details={
                    'title': 'Unattached Disk - Pure Digital Waste',
                    'recommendation': 'Delete it. Now.'
                }
            )
        ]
    
    def get_total_monthly_cost(self) -> float:
        return 4237.89
    
    def estimate_savings(self, waste_items: List[WasteItem]) -> float:
        return sum(item.potential_savings for item in waste_items)
