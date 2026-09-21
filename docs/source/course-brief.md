# Course brief — Intelligent Multi-Agent Traffic Management

**Source:** `SUMO_forStudents.docx`  
**Creator recorded in the source:** Akermi Hasni  
**Role in this repo:** the course authority for CoFlow-5 Synapse. Design Thinking stages, requirements, and Kiro specs must answer this brief.

## Project overview

Urban traffic congestion is a complex problem that changes continuously depending on the time, location, traffic demand, and unexpected events.

In this project, you will explore how Data Science and intelligent autonomous agents can be used to create a smarter traffic management system.

Your objective is to design a system in which intelligent agents can make decisions about traffic management based on the information available to them.

You will follow the Design Thinking methodology to understand the problem, identify relevant stakeholders and needs, explore possible solutions, build a prototype, and test your ideas.

## Challenge

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

You are free to investigate and decide:

- What information should an agent use?
- What decisions should it make?
- Should agents work independently or cooperate?
- How should their performance be evaluated?
- What Data Science or AI approaches could help?
- What additional factors could be considered beyond traffic flow?

There is no predefined technical solution. You are encouraged to research, experiment, compare approaches, learn from failures, and justify your choices.

## Expected outcome

By the end of the project, you should have:

- A working prototype of your proposed solution.
- Experiments demonstrating how it behaves under different traffic conditions.
- A comparison with an appropriate baseline or existing approach.
- Data-driven evidence showing the strengths and limitations of your solution.

Innovation, experimentation, reasoning, and evidence are more important than technological complexity.

## Think beyond traffic lights

The problem can potentially be extended to areas such as:

- emergency vehicles
- pedestrians
- public transportation
- sustainability
- pollution
- accident scenarios
- communication between agents
- prediction
- large-scale urban networks

The direction you take is part of the challenge.

## CoFlow-5 answer to the free questions

| Brief question | Settled answer |
|---|---|
| What information should an agent use? | Local SUMO observations plus typed, expiring, confidence-tagged advisory messages. |
| What decisions should it make? | A1 selects a legal signal action. A2–A5 request, forecast, alert, or advise. Synapse explains and never actuates. |
| Independent or cooperate? | Cooperate. One writer. Specialists ask. A1 arbitrates. |
| How is performance evaluated? | Paired seeds against fixed-time and actuated baselines, with stakeholder KPIs, ablations, failure injection, and honest null results. |
| Which Data Science or AI approaches? | Data lifecycle, EDA, Max-Pressure control, LightGBM forecasting, retrieval-grounded explanations. Reinforcement learning is optional. |
| Factors beyond traffic flow? | Emergency passage, pedestrian clearance, transit regularity, emission proxies, incidents, communication faults, and operator explainability. |
