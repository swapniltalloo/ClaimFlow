import networkx as nx
from typing import Dict, Any, List, Tuple


class ProviderGraphSignals:
    """Layer 4: NetworkX Graph Signals for provider-doctor-patient relationship clustering."""

    def __init__(self):
        self.graph = nx.Graph()

    def add_claim(self, hospital_id: str, doctor_name: str, patient_id: str, claim_id: str):
        """Adds nodes and edges representing the encounter."""
        self.graph.add_node(hospital_id, node_type="hospital")
        self.graph.add_node(doctor_name, node_type="doctor")
        self.graph.add_node(patient_id, node_type="patient")

        # Add connecting edges
        self.graph.add_edge(hospital_id, doctor_name)
        self.graph.add_edge(doctor_name, patient_id, claim_id=claim_id)

    def compute_graph_risk(self, hospital_id: str, doctor_name: str, patient_id: str) -> Tuple[float, List[str]]:
        """Calculates network topology anomaly score for a given triad.
        
        Returns:
            Tuple of (risk_score 0-100, reasons: List[str])
        """
        reasons = []
        base_score = 10.0

        if not self.graph.has_node(doctor_name) or not self.graph.has_node(hospital_id):
            return base_score, []

        doc_degree = self.graph.degree(doctor_name)

        # Unusual concentration of patient claims under one doctor
        if doc_degree > 50:
            base_score += 35.0
            reasons.append(f"High doctor degree centrality ({doc_degree} active patient connections)")

        # Short path repetition between patient and provider
        if self.graph.has_node(patient_id) and nx.has_path(self.graph, patient_id, hospital_id):
            shortest_path = nx.shortest_path_length(self.graph, patient_id, hospital_id)
            if shortest_path <= 2 and self.graph.degree(patient_id) > 5:
                base_score += 30.0
                reasons.append(f"Unusual high-frequency claim cycle for patient {patient_id}")

        return min(100.0, base_score), reasons
