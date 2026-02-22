# AEGIS: SURVEILLANCE & SOCIAL ENGINEERING SIMULATION

## 1. PROJECT OVERVIEW
Aegis is a modular simulation ecosystem designed to model urban social engineering, predictive surveillance, and population sentiment manipulation. The system utilizes autonomous agent-based modeling to track and influence the behavior of a populace in a fictional district.

The project is structured as a dual-application node system communicating via a shared JSON state layer.

---

## 2. TECHNICAL SPECIFICATIONS (v2.0)
* **Total Resolution:** 1600 x 1200 px
* **Active Simulation Map:** 1200 x 1200 px (1:1 Aspect Ratio)
* **UI Command Panel:** 400 x 1200 px
* **Target Frame Rate:** 60 FPS
* **Agent Density:** Optimized for 80+ concurrent autonomous entities

---

## 3. SYSTEM ARCHITECTURE

### A. Master Simulation Engine (Administrator)
The core engine manages the physical and psychological state of all agents within a 2D environment.
* **Agent Logic:** NPCs are modeled as autonomous entities with vectors for speed, position, and orientation. 
* **Psychological Variables:**
    * trust_level: A float value (0.0 - 1.0) representing the agent's confidence in the government.
    * hostility: Inversely proportional to trust. High hostility triggers unique behavioral states and "Riot" phrases.
    * has_app: A boolean determining if the agent is trackable via the digital footprint.

### B. Field Terminal (User Application)
A remote client providing a tactical interface for field operatives.
* **Authentication Layer:** Implements a GUI login interface utilizing a users.json personnel database. 
* **Satellite Uplink Simulation:** To simulate realistic high-latency data transfer, the minimap and terminal logs refresh on a 2.0s pulse interval.

---

## 4. MATHEMATICAL IMPLEMENTATION

### Coordinate Mapping
To display the high-resolution world (1200 x 1200) within the User App's compact minimap (410 x 250), a linear scaling transformation is applied:

X_user = X_offset + ( (X_admin / W_admin) * W_mini )
Y_user = Y_offset + ( (Y_admin / H_admin) * H_mini )

---

## 5. OPERATIONAL PROTOCOLS

### Surveillance and Targeting
* **Lerp Camera:** The camera utilizes Linear Interpolation to glide smoothly toward targeted entities.
* **Tactical Overlay:** When a target is locked via the Search Bar, a transparent pulse of the eye.png asset is rendered, centered on the entity's screen-space coordinates.

### Intervention Protocols
* **Seed Misinfo [R]:** Triggers a localized hostility spike. Trust levels drop to 0.0 for all agents within the pulse radius.
* **Counter Narrative [P]:** Broadcasts a "Truth Sync" to agents with the app installed, resetting trust to 1.0 and enforcing peace.

---

## 6. DATA STRUCTURES

### State Synchronization (aegis_state.json)
```json
{
  "recent_events": [
    {
      "type": "STRING",
      "pos": [INT, INT],
      "timestamp": "HH:MM:SS",
      "message": "STRING"
    }
  ],
  "heat_map": [
    [X_COORD, Y_COORD, HOSTILITY_VALUE]
  ],
  "world_dim": [1200, 1200]
}
### Personnel Database
```json
{
  "authorized_personnel": [
    {
      "username": "STRING",
      "password": "STRING",
      "role": "STRING",
      "clearance": "STRING"
    }
  ]
}

## 7. SETUP AND EXECUTION

### Dependencies: Install Pygame (pip install pygame).
### Asset Requirements: Ensure eye.png, users.json, and anothermap.png (1200x1200px) are in the root directory.
### Execution:
* ** Launch admin.py to initialize the simulation.
* ** Launch user.py to access the field terminal.
* ** Login: Enter credentials directly into the GUI. Use [TAB] to switch between Personnel ID and Access Key.
