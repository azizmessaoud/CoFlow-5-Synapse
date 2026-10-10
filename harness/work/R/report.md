# R report

The offline walkthrough indexes tagged evidence without launching SUMO. The
compose deployment separates a read-only FastAPI image from the React/nginx
image, mounts evidence read-only, and does not install a traffic simulator.
The native Windows smoke command remains separate from this deployment shape.
