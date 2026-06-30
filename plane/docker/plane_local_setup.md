# Plane local setup notes

## Goal

Run Plane locally as the project management system for COMPASS AI.

COMPASS AI will use Plane as an external task management system. Plane should be started and verified independently before integrating it with the COMPASS backend.

## Official sources

- GitHub: https://github.com/makeplane/plane
- Self-hosting overview: https://developers.plane.so/self-hosting/overview
- Docker Compose setup: https://developers.plane.so/self-hosting/methods/docker-compose

## Local strategy

- Keep Plane files inside `plane/docker`.
- Do not mix Plane containers with `docker-compose.compass.yml` yet.
- Start Plane first.
- Verify Plane in browser.
- Create local workspace `compass-ai-lab`.
- Later connect COMPASS AI through Plane API.

## Expected local workspace

Workspace:
- compass-ai-lab

Projects:
- Backend Platform
- Frontend Platform
- Data Platform
- Internal Tools

Statuses:
- Backlog
- Ready
- In Progress
- Review
- Done
- Blocked

Labels:
- backend
- frontend
- ml
- data
- devops
- bug
- feature
- refactoring
- urgent
- growth-task

## Notes

Exact Plane Docker Compose commands must follow the current official documentation because Plane self-hosting layout may change between releases.