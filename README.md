# <PROJECT NAME> AEGIS: SURVEILLANCE & SOCIAL ENGINEERING SIMULATION

A multi-application ecosystem developed to simulate urban social engineering, predictive surveillance, and population sentiment manipulation using Python and Pygame.
This repository contains the logic bridges, Python simulation scripts, and architectural configurations developed for the Aegis project.

The goal of this project is to practice agent-based modeling, real-time data synchronization between separate processes, and tactical UI design.

---

## Features Implemented
- Dual-application architecture (Admin Simulation and Field User Terminal)
- Autonomous Agent Logic with real-time Trust/Hostility variables
- Coordinate Mapping (1200x1200px world scaled to 410x250px minimap)
- Real-time JSON State Synchronization (aegis_state.json)
- Personnel Authentication System with password masking and field toggling
- Tactical Surveillance Overlay (Aegis Eye) with smooth Lerp camera tracking
- Modular Intervention Protocols (Seed Misinfo and Counter Narrative)
- Search and Track system with fuzzy matching for 80+ NPCs

---

## Technical Specifications (v2.0)
- Total Resolution: 1600 x 1200 px
- Active Simulation Map: 1200 x 1200 px (1:1 Aspect Ratio)
- UI Command Panel: 400 x 1200 px
- Satellite Uplink Pulse: 2.0s refresh interval for field terminal
- Framework: Python 3.x / Pygame / JSON Data Layer

---

## Skills Learned (Implementation Details)
- Agent-Based Modeling (ABM) fundamentals
- Inter-process communication via shared file states
- Linear Interpolation (Lerp) for cinematic camera movement
- 2D Coordinate Transformation and Scaling mathematics
- GUI Input handling (Text buffers, event polling, masking)
- Collision mask generation from urban environment bitmaps
- Social Engineering simulation (Contagious variable modeling)
- Modular software design for government/surveillance aesthetics

This project serves as a practical notebook of my implementation and understanding.

---

## Repository Structure
Large auto-generated folders, high-resolution environmental textures, and temporary state files are excluded to keep the repo lightweight and legal.

---

## How to Build / Run

1. Clone this repository  
2. Ensure Python 3.x and Pygame are installed (pip install pygame)
3. Ensure eye.png, users.json, and anothermap.png (1200x1200px) are in the root directory
4. Launch admin.py to initialize the simulation engine
5. Launch user.py to open the field terminal
6. Authenticate using credentials provided in users.json (Use [TAB] to toggle fields)

---
**END OF DOCUMENT**
