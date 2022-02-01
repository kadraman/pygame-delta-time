### A PyGame "delta time" example

This is an example [PyGame](https://www.pygame.org/) animation that uses 
"delta-time" to ensure that screen updates are unaffected by framerate. 

There are three sprites which move at different velocities (in this case pixels per second). It estimates
the expected time for each of the sprites to cross the screen and displays
the actual time. They should be approximately the same and more importantly
the same in any execution environment.
