"""
MRP (Material Requirements Planning) Service
Calculates material needs for production orders and identifies shortages.
Helps logists determine what materials to order and when.
"""

from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass
from models.order import ProductionOrderRepository
from models.material import MaterialRepository
from models.bom import BOMRepository
from models.production_plan import ProductionPlanRepository


@dataclass
class MaterialRequirement:
    """Represents a material requirement for procurement."""
    material_id: int
    material_name: str
    unit: str
    quantity_needed: float
    quantity_in_stock: float
    quantity_shortage: float  # negative means surplus, positive means shortage
    deadline: str  # when this material is needed (based on order start time)
    orders_requiring: List[int]  # list of order IDs that need this material
    
    def __str__(self) -> str:
        status = "✓ OK" if self.quantity_shortage <= 0 else f"⚠️  SHORTAGE"
        return f"{self.material_name} ({self.unit}): Need {self.quantity_needed}, Have {self.quantity_in_stock} [{status}]"


class MRPService:
    """Service to calculate material requirements and generate procurement plans."""
    
    @staticmethod
    def calculate_material_requirements() -> List[MaterialRequirement]:
        """
        Calculates all material requirements for pending production orders.
        Compares required materials with current stock.
        
        Returns:
            List of MaterialRequirement objects, one per material needed
        """
        print("\n" + "="*80)
        print("CALCULATING MATERIAL REQUIREMENTS")
        print("="*80)
        
        # Get all pending production orders
        pending_orders = ProductionOrderRepository.get_pending_orders()
        
        if not pending_orders:
            print("No pending orders - no material requirements")
            return []
        
        print(f"\n📋 Analyzing {len(pending_orders)} pending orders...")
        
        # Dictionary to accumulate material requirements
        # Key: material_id, Value: {name, unit, quantity_needed, in_stock, orders, earliest_deadline}
        material_reqs: Dict[int, Dict] = {}
        
        # Get all production plans to determine when materials are needed
        production_plans = ProductionPlanRepository.get_all_plans()
        
        # Process each pending order
        for order in pending_orders:
            # Get BOM entries (materials needed) for this product
            bom_entries = BOMRepository.get_bom_by_product_id(order.product_id)
            
            # Find when this order will be produced (from production plan)
            order_start_time = None
            for plan in production_plans:
                if plan.order_id == order.id and plan.status in ["planned", "in_progress"]:
                    order_start_time = plan.planned_start_time
                    break
            
            # For each material in the BOM
            for bom_entry in bom_entries:
                material = MaterialRepository.get_material_by_id(bom_entry.material_id)
                if not material:
                    continue
                
                # Calculate quantity needed for this order
                quantity_needed = bom_entry.quantity_needed * order.quantity
                
                # Add or update in material requirements
                if material.id not in material_reqs:
                    material_reqs[material.id] = {
                        "name": material.name,
                        "unit": material.unit,
                        "quantity_needed": 0,
                        "in_stock": material.quantity,
                        "orders": [],
                        "deadline": order_start_time if order_start_time else datetime.now().isoformat()
                    }
                
                material_reqs[material.id]["quantity_needed"] += quantity_needed
                material_reqs[material.id]["orders"].append(order.id)
                
                # Update deadline to earliest (soonest needed)
                if order_start_time:
                    current_deadline = datetime.fromisoformat(material_reqs[material.id]["deadline"])
                    order_deadline = datetime.fromisoformat(order_start_time)
                    if order_deadline < current_deadline:
                        material_reqs[material.id]["deadline"] = order_start_time
        
        # Create MaterialRequirement objects
        requirements: List[MaterialRequirement] = []
        
        for material_id, req in material_reqs.items():
            shortage = req["quantity_needed"] - req["in_stock"]
            
            req_obj = MaterialRequirement(
                material_id=material_id,
                material_name=req["name"],
                unit=req["unit"],
                quantity_needed=req["quantity_needed"],
                quantity_in_stock=req["in_stock"],
                quantity_shortage=shortage,
                deadline=req["deadline"],
                orders_requiring=req["orders"]
            )
            requirements.append(req_obj)
        
        print(f"\n✅ Material requirements calculated for {len(requirements)} materials")
        return requirements
    
    @staticmethod
    def generate_procurement_plan() -> Dict:
        """
        Generates a procurement plan for logists.
        Shows what materials need to be ordered and when.
        
        Returns:
            Dictionary with:
            - 'all_materials': all material requirements
            - 'shortage_materials': only materials with shortage
            - 'summary': counts and totals
        """
        print("\n" + "="*80)
        print("GENERATING PROCUREMENT PLAN FOR LOGISTS")
        print("="*80)
        
        # Get all material requirements
        all_requirements = MRPService.calculate_material_requirements()
        
        if not all_requirements:
            print("\nNo materials needed - no production planned")
            return {
                "all_materials": [],
                "shortage_materials": [],
                "summary": {
                    "total_materials": 0,
                    "materials_with_shortage": 0,
                    "total_shortage_value": 0
                }
            }
        
        # Filter materials with shortage
        shortage_materials = [r for r in all_requirements if r.quantity_shortage > 0]
        ok_materials = [r for r in all_requirements if r.quantity_shortage <= 0]
        
        print(f"\n📦 MATERIAL REQUIREMENTS SUMMARY:")
        print("-" * 80)
        print(f"   Total materials needed: {len(all_requirements)}")
        print(f"   Materials with shortage: {len(shortage_materials)}")
        print(f"   Materials with sufficient stock: {len(ok_materials)}")
        
        # Display materials with shortage (urgent for logists)
        if shortage_materials:
            print(f"\n🚨 URGENT - MATERIALS TO ORDER (SHORTAGE):")
            print("-" * 80)
            
            for req in shortage_materials:
                print(f"\n   📌 {req.material_name}")
                print(f"      ├─ Needed: {req.quantity_needed:.2f} {req.unit}")
                print(f"      ├─ In Stock: {req.quantity_in_stock:.2f} {req.unit}")
                print(f"      ├─ ORDER: {req.quantity_shortage:.2f} {req.unit}")
                print(f"      ├─ Deadline: {req.deadline}")
                print(f"      └─ For Orders: #{', #'.join(map(str, req.orders_requiring))}")
        
        # Display materials with sufficient stock
        if ok_materials:
            print(f"\n✅ MATERIALS WITH SUFFICIENT STOCK:")
            print("-" * 80)
            
            for req in ok_materials:
                surplus = -req.quantity_shortage
                print(f"   {req.material_name}: Have {req.quantity_in_stock:.2f} {req.unit}, Need {req.quantity_needed:.2f} {req.unit} (Surplus: {surplus:.2f} {req.unit})")
        
        # Summary for procurement team
        print(f"\n" + "="*80)
        print(f"PROCUREMENT SUMMARY FOR LOGISTS:")
        print("="*80)
        
        total_shortage_value = sum(r.quantity_shortage for r in shortage_materials)
        
        print(f"\n   Total materials with shortage: {len(shortage_materials)}")
        print(f"   Total units to order: {total_shortage_value:.2f}")
        
        if shortage_materials:
            # Group by deadline
            deadlines = {}
            for req in shortage_materials:
                deadline = req.deadline.split()[0]  # Get just the date
                if deadline not in deadlines:
                    deadlines[deadline] = []
                deadlines[deadline].append(req)
            
            print(f"\n   📅 ORDERED BY DEADLINE:")
            print("-" * 80)
            for deadline in sorted(deadlines.keys()):
                materials = deadlines[deadline]
                print(f"      {deadline}: {len(materials)} material(s) needed")
                for req in materials:
                    print(f"         - {req.material_name}: order {req.quantity_shortage:.2f} {req.unit}")
        
        print("\n" + "="*80)
        
        return {
            "all_materials": all_requirements,
            "shortage_materials": shortage_materials,
            "summary": {
                "total_materials": len(all_requirements),
                "materials_with_shortage": len(shortage_materials),
                "total_shortage_value": total_shortage_value
            }
        }
