import json
from typing import Dict, List, Optional
from datetime import datetime
import os
from pathlib import Path

class JSONStorage:
    def __init__(self, file_path: str = "db/agents.json"):
        self.file_path = file_path
        self.ensure_file_exists()

    def ensure_file_exists(self):
        """Ensure the storage file exists with proper permissions."""
        path = Path(self.file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            with open(self.file_path, 'w') as f:
                json.dump({"agents": []}, f)
        # Set permissions
        os.chmod(self.file_path, 0o666)
        os.chmod(path.parent, 0o777)

    def _read(self) -> Dict:
        """Read the current state from file."""
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _write(self, data: Dict) -> None:
        """Write the current state to file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def create_agent(self, agent_data: Dict) -> Dict:
        """Create a new agent."""
        data = self._read()
        
        # Generate new ID
        new_id = len(data["agents"]) + 1
        
        # Prepare agent data
        agent = {
            "id": new_id,
            **agent_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": None
        }
        
        # Add to storage
        data["agents"].append(agent)
        self._write(data)
        
        return agent

    def get_agent(self, agent_id: int) -> Optional[Dict]:
        """Get an agent by ID."""
        data = self._read()
        for agent in data["agents"]:
            if agent["id"] == agent_id:
                return agent
        return None

    def update_agent(self, agent_id: int, update_data: Dict) -> Optional[Dict]:
        """Update an existing agent."""
        data = self._read()
        
        for i, agent in enumerate(data["agents"]):
            if agent["id"] == agent_id:
                # Update fields
                agent.update(update_data)
                agent["updated_at"] = datetime.now().isoformat()
                data["agents"][i] = agent
                self._write(data)
                return agent
        
        return None

    def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent."""
        data = self._read()
        
        initial_length = len(data["agents"])
        data["agents"] = [a for a in data["agents"] if a["id"] != agent_id]
        
        if len(data["agents"]) < initial_length:
            self._write(data)
            return True
        return False

    def list_agents(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """List all agents with pagination."""
        data = self._read()
        return data["agents"][skip:skip + limit]
