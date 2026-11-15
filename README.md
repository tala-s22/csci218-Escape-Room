# CSCI218: AI Escape Room

Project structure:

- environment.py - Grid world and layout generator (Member 1)
- navigation.py - A* search (Member 2)
- agent.py - Adaptive Finite State Machine agent (Member 3)
- events.py - Dynamic events (Member 4)
- baseline.py - Non-adaptive baseline agent (Member 4)
- experiments.py - Experiment runner and charts (Member 5)
- visualise.py - Animated view for the demo (Member 5)
- main.py - Entry point (Member 5)
- tests/ - One test file per member

Install and run instructions will be added before submission.

## Conventions
- agent.path starts with the agent's current cell, so path[1] is the next cell to move to.
